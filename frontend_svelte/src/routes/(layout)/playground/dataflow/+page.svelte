<script lang="ts">
	import JsonData from '$components/JsonData.svelte';
	import type { PageProps } from './$types';
    import { enhance, applyAction  } from '$app/forms';
    import { type SubmitFunction } from '@sveltejs/kit';
	import { goto } from '$app/navigation';

	let { data, form }: PageProps = $props();

	console.log('=== playground - dataflow - +page.svelte ===');
    const dataWithoutBackEndConfiguration = Object.fromEntries(
        Object.entries(data).filter(([key]) => !key.startsWith('backendAPIConfiguration'))
    );
	console.log(dataWithoutBackEndConfiguration); // { layoutServerTs: 1, layout.ts: 2, pageServerTs: 3, pageTs: 4  }

    const redirect = () => {
        goto('dataflow/redirect');
    }

    const subTitleHeight = "min-h-[calc(3*var(--text-title-small--line-height))]"

    let resultOfSubmit = $state({});

    let success = $state(false)
    let fail = $state(false)

    // enhanced submit function:
    const submitFunction: SubmitFunction = async ( {formElement, formData, action, cancel, submitter} ) => {
        // Also a good place to show a loading indicator or similar.
        // Canceling form submission is also possible here.
        // Don't do form data validation here, as user can change client side JavaScript with browsers dev tools.
        console.log('=== playground - dataflow - submitFunction ===');
        console.log('formElement:', formElement);
        console.log('formData:', formData);
        console.log('action:', action);
        console.log('cancel:', cancel);
        console.log('submitter:', submitter);
    }

    // enhanced submit function with callback:
    const submitFunctionWithCallBack: SubmitFunction = async ( {formElement, formData, action, cancel, submitter} ) => {
        // Also a good place to show a loading indicator or similar.
        // Canceling form submission is also possible here.
        // Don't do form data validation here, as user can change client side JavaScript with browsers dev tools.
        console.log('=== playground - dataflow - submitFunctionWithCallback ===');
        console.log('formElement:', formElement);
        console.log('formData:', formData);
        console.log('action:', action);
        console.log('cancel:', cancel);
        console.log('submitter:', submitter);
        return async ( {result} ) => {
            // This callback is called after the form submission is complete.
            // A good place to update the user interface or show a success message and remove a potential loading indicator.
            resultOfSubmit = result;
            if (result.type === 'success') {
                // This is an expected error, so we can handle it here.
                // For example, show a message to the user.
                success = true;
            }
            console.log('=== playground - dataflow - submitFunctionWithCallback - result ===');
            console.log('result:', result);
        };
    }

    // enhanced submit function with callback and applyAction:
    const submitFunctionWithCallBackAndApplyAction: SubmitFunction = async ( {formElement, formData, action, cancel, submitter} ) => {
        // Also a good place to show a loading indicator or similar.
        // Canceling form submission is also possible here.
        // Don't do form data validation here, as user can change client side JavaScript with browsers dev tools.
        console.log('=== playground - dataflow - submitFunctionWithCallback ===');
        console.log('formElement:', formElement);
        console.log('formData:', formData);
        console.log('action:', action);
        console.log('cancel:', cancel);
        console.log('submitter:', submitter);
        return async ( {result} ) => {
            // This callback is called after the form submission is complete.
            // A good place to update the user interface or show a success message and remove a potential loading indicator.
            resultOfSubmit = result;
            console.log('=== playground - dataflow - submitFunctionWithCallback - result ===');
            console.log('result:', result);
            applyAction( result )
        };
    }

    // enhanced submit function with callback and applyAction:
    const submitFunctionWithCallBackAndUpdate: SubmitFunction = async ( {formElement, formData, action, cancel, submitter} ) => {
        // Also a good place to show a loading indicator or similar.
        // Canceling form submission is also possible here.
        // Don't do form data validation here, as user can change client side JavaScript with browsers dev tools.
        console.log('=== playground - dataflow - submitFunctionWithCallback ===');
        console.log('formElement:', formElement);
        console.log('formData:', formData);
        console.log('action:', action);
        console.log('cancel:', cancel);
        console.log('submitter:', submitter);
        return async ( {result, update} ) => {
            // This callback is called after the form submission is complete.
            // A good place to update the user interface or show a success message and remove a potential loading indicator.
            resultOfSubmit = result;
            console.log('=== playground - dataflow - submitFunctionWithCallback - result ===');
            console.log('result:', result);
            await update();
        };
    }

    const submitFunctionWhereExpectedErrorCausesFail: SubmitFunction = async ( {formElement, formData, action, cancel, submitter} ) => {
        // Also a good place to show a loading indicator or similar.
        // Canceling form submission is also possible here.
        // Don't do form data validation here, as user can change client side JavaScript with browsers dev tools.
        console.log('=== playground - dataflow - submitFunctionWithCallback ===');
        console.log('formElement:', formElement);
        console.log('formData:', formData);
        console.log('action:', action);
        console.log('cancel:', cancel);
        console.log('submitter:', submitter);
        return async ( {result, update} ) => {
            // This callback is called after the form submission is complete.
            // A good place to update the user interface or show a success message and remove a potential loading indicator.
            resultOfSubmit = result;
            console.log('=== playground - dataflow - submitFunctionWithCallback - result ===');
            console.log('result:', result);
            if (result.type === 'failure') {
                // This is an expected error, so we can handle it here.
                // For example, show a message to the user.
                fail = true;
            }
            await update();
        };
    }

    // difference between update() and applyAction():
    // applyAction() does not invalidate form data, update() does.
</script>

<div>
	<p class="title">+page.svelte</p>
	<JsonData data={dataWithoutBackEndConfiguration} />
</div>

<div class="text-center">
    <div class="heading">➡️ Redirect ➡️</div>
    <p class="p-4">Client side navigation to <button class="btn ml-10" onclick={redirect}>redirect page</button></p>
</div>

<!-- When using named actions, the default action cannot be used. -->
<!-- <form method="post">
    <p class="title">Default</p>
    <p class="title-small">HTML only/p>
    <div class="flex flex-row items-end gap-2">
        <div class="input-filled grow">
            <label class="input-filled-label" for="inputDefault">Default action</label>
            <input class="input input-sm" placeholder="send data to server" type="text" id="inputDefault" name="inputDefault" />
        </div>
        <button class="btn">Send</button>
    </div>
</form> -->

<form class="outline rounded p-2 m-2"method="post" action="?/named">
    <p class="title">Named</p>
    <p class="title-small {subTitleHeight}">HTML only</p>
    <div class="flex flex-row items-end gap-2">
        <div class="input-filled input-secondary grow">
        <label class="input-filled-label" for="inputNamed">Named action</label>
            <input class="input input-sm" placeholder="send data to server" type="text" id="inputNamed" name="inputNamed" />
        </div>
        <button class="btn btn-secondary">Send</button>
    </div>
</form>

<form class="outline rounded p-2 m-2" method="post" action="?/enhanced" use:enhance>
    <p class="title">Use:enhance</p>
    <p class="title-small {subTitleHeight}">default</p>
    <div class="flex flex-row items-end gap-2">
        <div class="input-filled input-accent grow">
        <label class="input-filled-label" for="inputEnhanced">Enhanced action</label>
            <input class="input input-sm" placeholder="send data to server" type="text" id="inputEnhanced" name="inputEnhanced" />
        </div>
        <button class="btn btn-accent">Send</button>
    </div>
</form>

<form class="outline rounded p-2 m-2" method="post" action="?/submitFunction" use:enhance={submitFunction}>
    <p class="title">Use:enhance</p>
    <p class="title-small {subTitleHeight}">Submit Function</p>
    <div class="flex flex-row items-end gap-2">
        <div class="input-filled input-neutral grow">
        <label class="input-filled-label" for="inputSubmit">Submit Function</label>
            <input class="input input-sm" placeholder="send data to server" type="text" id="inputSubmit" name="inputSubmit" />
        </div>
        <button class="btn btn-neutral">Send</button>
    </div>
</form>

<form class="outline rounded p-2 m-2" method="post" action="?/submitFunctionWithCallback" use:enhance={submitFunctionWithCallBack}>
    <p class="title">Use:enhance</p>
    <p class="title-small {subTitleHeight}">Submit Function with Callback
        {#if success}
            <span class="badge badge-success">Input successful</span>
        {/if}
    </p>
    <div class="flex flex-row items-end gap-2">
        <div class="input-filled input-neutral grow">
        <label class="input-filled-label" for="inputSubmitWithCallback">Submit Function with Callback</label>
            <input class="input input-sm" placeholder="send data to server" type="text" id="inputSubmitWithCallback" name="inputSubmitWithCallback" />
        </div>
        <button class="btn btn-neutral">Send</button>
    </div>
</form>

<form class="outline rounded p-2 m-2" method="post" action="?/submitFunctionWithCallBackAndApplyAction" use:enhance={submitFunctionWithCallBackAndApplyAction}>
    <p class="title">Use:enhance</p>
    <p class="title-small {subTitleHeight}">Submit Function with Callback and applyAction()</p>
    <div class="flex flex-row items-end gap-2">
        <div class="input-filled input-info grow">
        <label class="input-filled-label" for="inputSubmitWithCallBackAndApplyAction">SubmitFct, callback, applyAction</label>
            <input class="input input-sm" placeholder="send data to server" type="text" id="inputSubmitWithCallBackAndApplyAction" name="inputSubmitWithCallBackAndApplyAction" />
        </div>
        <button class="btn btn-info">Send</button>
    </div>
</form>

<form class="outline rounded p-2 m-2" method="post" action="?/submitFunctionWithCallBackAndUpdate" use:enhance={submitFunctionWithCallBackAndUpdate}>
    <p class="title">Use:enhance</p>
    <p class="title-small {subTitleHeight}">Submit Function with Callback and update()</p>
    <div class="flex flex-row items-end gap-2">
        <div class="input-filled input-success grow">
        <label class="input-filled-label" for="inputSubmitFunctionWithCallBackAndUpdateubmitUpdate">SubmitFct, callback, update</label>
            <input class="input input-sm" placeholder="send data to server" type="text" id="inputSubmitFunctionWithCallBackAndUpdate" name="inputSubmitFunctionWithCallBackAndUpdate" />
        </div>
        <button class="btn btn-success">Send</button>
    </div>
</form>

<form class="outline rounded p-2 m-2" method="post" action="?/redirectServerSide" use:enhance>
    <p class="title">Redirect server side</p>
    <p class="title-small {subTitleHeight}">Redirect through Svelte redirect() in action</p>
    <div class="flex flex-row items-end gap-2">
        <div class="input-filled input-error grow">
        <label class="input-filled-label" for="inputRedirectServerSide">Trigger redirect() on server</label>
            <input class="input input-sm" placeholder="send data to server" type="text" id="inputRedirectServerSide" name="inputRedirectServerSide" />
        </div>
        <button class="btn btn-error">Send</button>
    </div>
</form>

<form class="outline rounded p-2 m-2" method="post" action="?/expectedErrorCausesFail" use:enhance={submitFunctionWhereExpectedErrorCausesFail}>
    <p class="title">Expected error in action</p>
    <p class="title-small {subTitleHeight}">Returns fail() from action
        {#if fail}
            <span class="badge badge-error">Failed input</span>
        {/if}
    </p>
    <div class="flex flex-row items-end gap-2">
        <div class="input-filled input-warning grow">
        <label class="input-filled-label" for="inputExpectedErrorCausesFail">Trigger fail() on server</label>
            <input class="input input-sm" placeholder="send data to server" type="text" id="inputExpectedErrorCausesFail" name="inputExpectedErrorCausesFail" />
        </div>
        <button class="btn btn-warning">Send</button>
    </div>
</form>

<form class="outline rounded p-2 m-2" method="post" action="?/unexpectedErrorInBackend" use:enhance>
    <p class="title">Unexpected error in backend</p>
    <p class="title-small {subTitleHeight}">Throwing Error() in action and handle redirect through Svelte error() to <code>+error.svelte</code></p>
    <div class="flex flex-row items-end gap-2">
        <div class="input-filled input-error grow">
        <label class="input-filled-label" for="inputUnexpectedErrorInBackend">Trigger error() on server</label>
            <input class="input input-sm" placeholder="send data to server" type="text" id="inputUnexpectedErrorInBackend" name="inputUnexpectedErrorInBackend" />
        </div>
        <button class="btn btn-error">Send</button>
    </div>
</form>

<div>
    <p class="title">Form prop (same as page.form)</p>
    <JsonData data={form} />
</div>

<div>
    <p class="title">Submit Function <code>&#123;result&#125;</code></p>
    <JsonData data={resultOfSubmit} />
</div>

<div>
    <p class="title">Fail state</p>
    {#if form?.error}
        <p class="text-error">{form.error}</p>
    {/if}
</div>