import { beforeEach, describe, expect, test, vi } from 'vitest';

const redis = vi.hoisted(() => ({
	isOpen: true,
	on: vi.fn(),
	eval: vi.fn(),
	connect: vi.fn()
}));

vi.mock('redis', () => ({ createClient: () => redis }));
vi.mock('$app/environment', () => ({ building: false }));
vi.mock('./config', () => ({
	default: {
		getInstance: () =>
			Promise.resolve({
				redis_session_password: 'test',
				redis_host: 'cache',
				redis_port: 6379,
				redis_session_db: 0,
				session_timeout: 3600,
				encryption: {
					keys: [{ version: 'test', key: Uint8Array.from({ length: 32 }, () => 1) }]
				}
			})
	}
}));

describe('RedisCache renewal', () => {
	beforeEach(() => vi.clearAllMocks());

	test('atomically renews concurrent attempts without using a key-creating command', async () => {
		redis.eval.mockResolvedValueOnce(1).mockResolvedValueOnce(0);
		const { redisCache } = await import('./cache');

		await expect(
			Promise.all([
				redisCache.renewSessionIfNeeded('session-1'),
				redisCache.renewSessionIfNeeded('session-1')
			])
		).resolves.toEqual(['renewed', 'unchanged']);
		const script = redis.eval.mock.calls[0][0] as string;
		expect(script).toContain("redis.call('TTL', KEYS[1])");
		expect(script).toContain("redis.call('EXPIRE', KEYS[1], ARGV[2])");
		expect(script).not.toMatch(/redis\.call\(['"]SET['"]/);
	});

	test('does not recreate a missing session', async () => {
		redis.eval.mockResolvedValueOnce(-1);
		const { redisCache } = await import('./cache');

		await expect(redisCache.renewSessionIfNeeded('missing')).resolves.toBe('missing');
	});
});
