import { type BrowserContext, chromium, type Page, test } from '@playwright/test';

const stageUrl = process.env.STAGE_FRONTEND_URL?.replace(/\/$/, '');
const endpoint = '/presentation/34654/e26/introduction';
// higher levels merely test the power of localhost,
// but not the server side,
// as all of these connections need to render a full browser loaded page!
const concurrencyLevels = [10]; //[5, 10, 20, 40, 60];
const warmupHoldMs = 5_000;
const levelHoldMs = 30_000;

// Drop rendering-heavy resources: this is an end-to-end load check, not a visual test.
const blockedResource =
	/\.(png|jpe?g|gif|webp|svg|ico|woff2?|ttf)(\?|$)|fonts\.(googleapis|gstatic)\.com/i;

async function blockHeavyResources(target: Page | BrowserContext) {
	await target.route(blockedResource, (route) => route.abort());
}

// The aborts above surface as failed requests; they are intentional, not server errors.
function isBlockedResource(url: string) {
	return blockedResource.test(url);
}

test('loads a public presentation in staging environment', async () => {
	test.setTimeout(20 * 60 * 1_000);

	if (!stageUrl) {
		throw new Error('STAGE_FRONTEND_URL must be set for the stage stress test.');
	}

	const url = `${stageUrl}${endpoint}`;
	const browser = await chromium.launch({
		executablePath: '/usr/bin/chromium',
		args: ['--disable-gpu', '--disable-dev-shm-usage', '--no-sandbox']
	});
	const warmupPage = await browser.newPage();
	await blockHeavyResources(warmupPage);
	await warmupPage.goto(url, { waitUntil: 'domcontentloaded', timeout: 120_000 });
	await warmupPage.waitForTimeout(warmupHoldMs);
	await warmupPage.close();

	for (const concurrency of concurrencyLevels) {
		const contexts = await Promise.all(
			Array.from({ length: concurrency }, () => browser.newContext())
		);
		await Promise.all(contexts.map((context) => blockHeavyResources(context)));
		const pages = await Promise.all(contexts.map((context) => context.newPage()));
		const errors: string[] = [];

		for (const [pageIndex, page] of pages.entries()) {
			page.on('pageerror', (error) => errors.push(`page ${pageIndex} pageerror: ${error.message}`));
			page.on('requestfailed', (request) => {
				if (isBlockedResource(request.url())) return;
				errors.push(
					`page ${pageIndex} requestfailed: ${request.url()} (${request.failure()?.errorText})`
				);
			});
			page.on('console', (message) => {
				if (message.type() === 'error' && !message.text().includes('Failed to load resource')) {
					errors.push(`page ${pageIndex} console: ${message.text()}`);
				}
			});
		}

		try {
			const results = await Promise.allSettled(
				pages.map(async (page, pageIndex) => {
					const response = await page.goto(url, {
						waitUntil: 'domcontentloaded',
						timeout: 120_000
					});
					if (!response || response.status() >= 400) {
						errors.push(`page ${pageIndex} HTTP status: ${response?.status() ?? 'none'}`);
					}
				})
			);

			results.forEach((result, pageIndex) => {
				if (result.status === 'rejected') {
					errors.push(`page ${pageIndex} navigation: ${result.reason}`);
				}
			});
			await new Promise((resolve) => setTimeout(resolve, levelHoldMs));
			console.log(`stage stress: ${concurrency} pages, ${errors.length} observed errors`);
			errors.forEach((error) => console.log(`  ${error}`));
		} finally {
			await Promise.all(contexts.map((context) => context.close()));
		}
	}

	await browser.close();
});
