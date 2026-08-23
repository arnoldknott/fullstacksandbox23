import { SvelteSet } from 'svelte/reactivity';

import { Action } from './accessHandler';
import type { AccessPolicy, AnyEntityExtended, Hierarchy, Identity } from './types';

/**
 * For managing new entities before submitting them,
 * they are alive in the frontend only and EntityContainer holds space for them.
 */
type PendingConfiguration<T extends AnyEntityExtended = AnyEntityExtended> = {
	parentId?: string; // should it be here?
	inherit?: boolean;
	public?: boolean;
	publicAction?: Action;
	template?: Partial<Omit<T, 'id'>>;
};

export type EntityContainerConfiguration<T extends AnyEntityExtended = AnyEntityExtended> = Partial<
	PendingConfiguration<T>
>;
// 	EntityData<T> & PendingConfiguration<T>
// >;

export interface EntityContainerInterface<T extends AnyEntityExtended = AnyEntityExtended> {
	entities: T[];
	pendingEntities: T[];
	identities: Identity[];
	// TBD: when payload separated from metadta, these should track the metadata:
	accessPolicies: Record<string, AccessPolicy[]>;
	accessRights: Record<string, Action>;
	hierarchies: Record<string, Hierarchy[]>;
	selections: Record<string, string[]>;
	parentId?: string | null;
	pendingTemplate?: Partial<Omit<T, 'id'>>;
	pendingSubmitOptions?: {
		parentId?: string;
		inherit?: boolean;
		public?: boolean;
		publicAction?: Action;
	};
	// Pending handling:
	createPending(overrides?: Partial<T>): T;
	// Selection handling:
	addSelection(name: string, entityIds: string[]): string[];
	removeSelection(name: string): void;
	addToSelection(name: string, entityIds: string[]): string[];
	removeFromSelection(name: string, entityIds: string[]): string[];
	getSelectedEntities(name?: string): T[];
	getSelectedIdentities(name?: string): Identity[];
	// Helper functions to creater specific selections:
	createFilteredEntitySelection(name: string, filterFn: (entity: T) => boolean): () => T[];
	createLinkedSelection(
		name: string,
		inverse: boolean,
		parentId: string,
		fromOtherSelection?: string
	): () => T[];
	createUserHasSpecificAccessRightSelection(
		name: string,
		action: Action,
		fromOtherSelection?: string
	): () => T[];
	createAccessPolicyResourceSelection(
		name: string,
		policyFilterFn: (policy: AccessPolicy) => boolean,
		fromOtherSelection?: string
	): () => T[];
	createAccessPolicyIdentitySelection(
		name: string,
		policyFilterFn: (policy: AccessPolicy) => boolean,
		fromOtherSelection?: string
	): () => Identity[];
	// Modifying selections:
	createSortedSelection(
		name: string,
		attribute: keyof T,
		ascending?: boolean,
		fromOtherSelection?: string
	): () => T[];
}

/**
 * Class that manages the entity data and related state,
 * that is pending entities, identities, access policies and rights, hierarchies, selections.
 * Provides methods to create pending entities, manage selections, and sort entities.
 * The EntityContainer is designed to be flexible and can be configured with initial data and
 * templates for pending entities.
 * Entities can both be resources and identites, whereas the sepearate identities are related to the
 */
export class EntityContainer<
	T extends AnyEntityExtended = AnyEntityExtended
> implements EntityContainerInterface<T> {
	// Data:
	#entities = $state<T[]>([]); // AnyEntityExtended[];
	#pendingEntities = $state<T[]>([]); // AnyEntityExtended[];
	#identities = $state<Identity[]>([]); // Identity[];
	// Metadata:
	#accessPolicies = $state<Record<string, AccessPolicy[]>>({}); // UUID: AccessPolicy[]
	#accessRights = $state<Record<string, Action>>({}); // UUID: Action
	#hierarchies = $state<Record<string, Hierarchy[]>>({}); // array of all parent and child hierarchies
	// Collection of generic selections to manage subsests of data potentially based on specific metadata criteria:
	#selections = $state<Record<string, string[]>>({}); // selectionName: entityIds[]
	parentId?: string | null;
	pendingTemplate?: Partial<Omit<T, 'id'>>; // AnyEntityExtended without id;
	pendingSubmitOptions?: {
		parentId?: string;
		inherit?: boolean;
		public?: boolean;
		publicAction?: Action;
	};

	constructor(configuration: EntityContainerConfiguration<T> = {}) {
		this.parentId = configuration.parentId ?? undefined;
		this.pendingTemplate = configuration.template ?? undefined;
		this.pendingSubmitOptions = {
			parentId: configuration.parentId ?? undefined,
			inherit: configuration.inherit ?? false,
			public: configuration.public ?? false,
			publicAction: configuration.publicAction ?? undefined
		};
	}

	// --- reactive surface ---
	/**
	 * Getters and Setters for the main entities array managed by this SocketIO instance.
	 *
	 * Deeply reactive array of entities managed by this socketio class.
	 * Read in templates, mutate in place, or reassign.
	 */
	get entities(): T[] {
		return this.#entities;
	}
	set entities(value: T[]) {
		this.#entities = value;
	}

	/** Reactive collection of entities that are being prepared but not yet submitted. */
	get pendingEntities(): T[] {
		return this.#pendingEntities;
	}
	set pendingEntities(value: T[]) {
		this.#pendingEntities = value;
	}

	get identities(): Identity[] {
		return this.#identities;
	}
	set identities(value: Identity[]) {
		this.#identities = value;
	}

	get accessPolicies(): Record<string, AccessPolicy[]> {
		return this.#accessPolicies;
	}
	set accessPolicies(value: Record<string, AccessPolicy[]>) {
		this.#accessPolicies = value;
	}

	get accessRights(): Record<string, Action> {
		return this.#accessRights;
	}
	set accessRights(value: Record<string, Action>) {
		this.#accessRights = value;
	}

	get hierarchies(): Record<string, Hierarchy[]> {
		return this.#hierarchies;
	}
	set hierarchies(value: Record<string, Hierarchy[]>) {
		this.#hierarchies = value;
	}

	get selections(): Record<string, string[]> {
		return this.#selections;
	}
	set selections(value: Record<string, string[]>) {
		this.#selections = value;
	}

	/**
	 * Produce a new entity with a preliminary `new_*` id (which the backend
	 * swaps for a real UUID on `status:created`.
	 * Merges, in order: the configured `pendingTemplate` (if any),
	 * then the optional `overrides` argument, then the freshly-generated id.
	 *
	 * Does not touch `entities` — callers either wrap the result in `$state(...)` to bind
	 * to form inputs and submit via {@link submitEntity} when ready.
	 */
	createPending(overrides?: Partial<T>): T {
		const pendingEntity = {
			...this.pendingTemplate,
			...overrides,
			id: 'new_' + Math.random().toString(36).substring(2, 9)
		} as T;
		this.#pendingEntities.unshift(pendingEntity);
		return pendingEntity;
	}

	/**
	 * Add an access policy for a pending entity to the accessPolicies collection.
	 * The accessPolicies collection stores all access policies for entities
	 * After submission and creation of the entity in the backend,
	 * the pending access policies - identified by the "new_" prefix in the id
	 * can be sent to the backend via a share method for processing.
	 */
	addPendingAccessPolicy(
		entityId: string,
		policy: AccessPolicy | Omit<AccessPolicy, 'resource_id'>
	) {
		if (entityId.startsWith('new_')) {
			if (!this.#accessPolicies[entityId]) {
				this.#accessPolicies[entityId] = [];
			}
			// replace existing pending or create new pending access policy for the entity
			// TBD: check if this covers public, where identity_id is undefined, and if it should be handled differently!
			const existingIndex = this.#accessPolicies[entityId].findIndex(
				(p) => p.identity_id == policy.identity_id
			);
			if (existingIndex !== -1) {
				this.#accessPolicies[entityId][existingIndex] = { resource_id: entityId, ...policy };
			} else {
				this.#accessPolicies[entityId].push({ resource_id: entityId, ...policy });
			}
		}
	}

	/**
	 * Add an access policy for a pending entity to the accessPolicies collection.
	 * The accessPolicies collection stores all access policies for entities
	 * After submission and creation of the entity in the backend,
	 * the pending access policies - identified by the "new_" prefix in the id
	 * can be sent to the backend via a share method for processing.
	 */
	addPendingHierarchy(entityId: string, hierarchy: Hierarchy | Omit<Hierarchy, 'child_id'>) {
		if (entityId.startsWith('new_')) {
			if (!this.#hierarchies[entityId]) {
				this.#hierarchies[entityId] = [];
			}
			// replace existing pending or create new pending access policy for the entity
			// TBD: check if this covers public, where identity_id is undefined, and if it should be handled differently!
			const existingIndex = this.#hierarchies[entityId].findIndex(
				(p) =>
					p.parent_id == hierarchy.parent_id &&
					p.child_id == ('child_id' in hierarchy ? hierarchy.child_id : entityId)
			);
			if (existingIndex !== -1) {
				this.#hierarchies[entityId][existingIndex] = { child_id: entityId, ...hierarchy };
			} else {
				this.#hierarchies[entityId].push({ child_id: entityId, ...hierarchy });
			}
		}
	}

	/** SELECTION MANAGEMENT **/

	/**
	 * Selections are named subsets of the main entity-id array, stored as arrays of ids.
	 *
	 * Deeply reactive array of an array of ids.
	 * Read in templates, mutate in place, or reassign.
	 * Use cases for selections might include:
	 * - marking the entities, that are editable in browser
	 * - marking the entities that are selected in a list for bulk actions
	 * - order of entities, that are sorted by a specific entity attribute
	 * - select by access policies: all entities that are shared with a specific team with a specific right, etc.
	 * - select by access rights: all entities that the user has 'own', 'write', 'connect' 'read' access to, etc.
	 * - select by hierarchy: all entities that are linked to a specific parent entity or have a specific child entity, etc.
	 */

	/**
	 * Add a selection to the entity container and optinally add initial entity ids to the selection.
	 *
	 * @param name of selection
	 * @param entityIds to add to the selection
	 * @returns the id's in the newly created selection
	 */
	addSelection(name: string, entityIds: string[] = []) {
		if (this.#selections[name]) {
			throw new Error(`Selection with name "${name}" already exists.`);
		}
		this.#selections[name] = entityIds;
		return this.#selections[name];
	}

	/**
	 * Removes the selection with the specified name from the entity container.
	 *
	 * @param name of selection to remove.
	 */
	removeSelection(name: string) {
		if (!this.#selections[name]) {
			throw new Error(`Selection with name "${name}" does not exist.`);
		}
		delete this.#selections[name];
	}

	/**
	 * Add the specified entity ids to the selection with the specified name.
	 * Mutates the selection in place by adding the new entity ids to the existing ones.
	 * Can also be used to preseed the selection with initial entity ids
	 *  when creating the selection with {@link addSelection} and
	 * then adding more entity ids later with this function.
	 *
	 * @param name of selection to which the entity ids should be added
	 * @param entityIds array of entity ids to add to the selection
	 * @returns the updated array of entity ids in the selection
	 */
	addToSelection(name: string, entityIds: string[]) {
		if (!this.#selections[name]) {
			throw new Error(`Selection with name "${name}" does not exist.`);
		}
		this.#selections[name] = [...this.#selections[name], ...entityIds];
		return this.#selections[name];
	}

	/**
	 * Removes the specified entity ids from the selection with the specified name.
	 *
	 * @param name of selection from which the entity ids should be removed
	 * @param entityIds array of entity ids to remove from the selection
	 * @returns the updated array of entity ids in the selection
	 */
	removeFromSelection(name: string, entityIds: string[]) {
		if (!this.#selections[name]) {
			throw new Error(`Selection with name "${name}" does not exist.`);
		}
		this.#selections[name] = this.#selections[name].filter((id) => !entityIds.includes(id));
		return this.#selections[name];
	}

	/** LINKED SELECTIONS TO DATA: Entities and Identities */

	/**
	 * Gets all entities that match this specific selection with its assigned selection function
	 *
	 * Call with $derived.by(() => entityContainer.getSelectedEntities('mySelection'))
	 * in caller to reactively get the selected entities for this selection.
	 * @param name specifies which selection to retrieve
	 * @returns the entities that correlate to the specified selection
	 */
	getSelectedEntities(name?: string): T[] {
		if (name) {
			const selectedIds = this.selections[name] ?? [];
			// ((entity) => selectedIds.includes(entity.id));
			// return this.selections[name].map((id) => this.entities.filter((entity) => entity.id === id)[0])
			// const selectedIds = this.selections[name] ?? [];
			// const entitiesById = new SvelteMap(this.entities.map((entity) => [entity.id, entity]));
			// return selectedIds
			// 	.map((id) => entitiesById.get(id))
			// 	.filter((entity): entity is T => entity !== undefined);
			const entitiesById = Object.fromEntries(
				this.entities.map((entity) => [entity.id, entity] as const)
			) as Record<string, T>;

			return selectedIds
				.map((id) => entitiesById[id])
				.filter((entity): entity is T => entity !== undefined);
		} else {
			return this.entities;
		}
	}

	/**
	 * Gets all identities that match this specific selection with its assigned selection function
	 *
	 * @param name specifies which selection to retrieve
	 * @returns the identities that correlate to the specified selection
	 */
	getSelectedIdentities(name?: string): Identity[] {
		if (name) {
			const selectedIds = this.selections[name] ?? [];
			// return this.identities.filter((identity) => selectedIds.includes(identity.id));
			// const selectedIds = this.selections[name] ?? [];
			// const identitiesById = new SvelteMap(
			// 	this.identities.map((identity) => [identity.id, identity])
			// );
			// return selectedIds
			// 	.map((id) => identitiesById.get(id))
			// 	.filter((identity): identity is AnyIdentityExtended => identity !== undefined);
			const identitiesById = Object.fromEntries(
				this.identities.map((identity) => [identity.id, identity] as const)
			) as Record<string, Identity>;

			return selectedIds
				.map((id) => identitiesById[id])
				.filter((identity): identity is Identity => identity !== undefined);
		} else {
			return this.identities;
		}
	}

	/**
	 * Generic internal method to create a reactive selection based on a filter function.
	 * The effectFunction should set the selection with the filtered entity ids.
	 *
	 * @param name of selection to create
	 * @param effectFunction the logic to create the selection,
	 * which typically filters the entities based on specific criteria and
	 * sets the selection with the resulting entity ids.
	 * It should set the selection with the filtered entity or identity ids.
	 * @returns the selected entities or identities based on the filter function,
	 * that updates reactively when entities or hierarchies change
	 *
	 */
	private createReactiveSelection(name: string, effectFunction: () => void) {
		this.addSelection(name);
		$effect(() => effectFunction());
		return () => this.getSelectedEntities(name);
	}

	// for example all entities that match a specific condition
	// TBD: extend with choosing different data containers, such as
	// accessPolicies, hierarchies, etc. for more complex selection logic,
	// e.g. select all entities that are shared with a specific team with a specific right,
	// or select all entities that are linked to a specific parent entity or have a specific child entity, etc.
	/**
	 *
	 * @param name of the selection to create
	 * @param filterFn function to filter the entities
	 * @param fromOtherSelection if provided, it will filter the entities
	 * from the specified selection instead of all entities.
	 * @returns a derived array of the selected entities,
	 * that updates reactively when entities or hierarchies change
	 *
	 * Uses {@link createReactiveSelection} for reactive updates when data or metadata changes.
	 */
	createFilteredEntitySelection(
		name: string,
		filterFn: (entity: T) => boolean,
		fromOtherSelection: string | undefined = undefined
	) {
		return this.createReactiveSelection(name, () => {
			this.#selections[name] = this.getSelectedEntities(fromOtherSelection)
				.filter(filterFn)
				.map((entity) => entity.id);
		});
	}

	/**
	 * Select all entities that are linked to a specific parent entity.
	 *
	 * @param name specifies the name of the selection.
	 * @param parentId specifies the parent entity to which the linked child entities belong.
	 * If not provided, it will use the EntityContainer's parentId property.
	 * If that is also not provided, it will throw an error.
	 * @param initialIds preseeds the selection with the specified entity ids,
	 * which is useful to prevent a "flash" of an empty selection before the effect runs
	 * and fills the selection with the correct linked entities.
	 * This can happen if the selection is rendered before the hierarchies
	 * and entities are loaded and the effect runs.
	 * @param inverse if set to true, it will select all entities that are NOT linked to the specified parent entity.
	 * @returns a derived array of the selected entities, that updates reactively when entities or hierarchies change
	 *
	 * Uses {@link createReactiveSelection} for reactive updates when data or metadata changes.
	 */
	createLinkedSelection(
		name: string,
		inverse: boolean = false,
		parentId: string = this.parentId
			? this.parentId
			: (() => {
					throw new Error(
						"Parent ID must be provided either as an argument or as the EntityContainer's parentId property."
					);
				})(),
		fromOtherSelection?: string
	) {
		return this.createReactiveSelection(name, () => {
			this.#selections[name] = this.getSelectedEntities(fromOtherSelection)
				.filter((entity) => {
					if (!inverse)
						// check if the parent_id matches the specified parentId
						return this.hierarchies[entity.id]?.some(
							(hierarchy) => hierarchy.parent_id === parentId
						);
					else
						// check if the parent_id does not match the specified parentId
						return this.hierarchies[entity.id]?.every(
							(hierarchy) => hierarchy.parent_id !== parentId
						);
				})

				.map((entity) => entity.id);
		});
	}

	/**
	 * Creates a selection of all entities that the user has a specific access right to,
	 * for example all entities that the user has 'own' access to, etc.
	 *
	 * @param name of the selection to create
	 * @param action the specific access right to filter entities by
	 * @param fromOtherSelection optional name of another selection to filter from
	 * @returns a derived array of the selected entities, that updates reactively when entities or access rights change
	 *
	 * Uses {@link createReactiveSelection} for reactive updates when data or metadata changes.
	 */
	createUserHasSpecificAccessRightSelection(
		name: string,
		action: Action,
		fromOtherSelection: string | undefined = undefined
	) {
		return this.createReactiveSelection(name, () => {
			this.#selections[name] = this.getSelectedEntities(fromOtherSelection)
				.filter((entity) => this.accessRights[entity.id] === action)
				// .filter((entity) => {
				//     // console.log("=== Filtering entities for access right selection ===")
				//     // console.log("Entity:", entity)
				//     return entity.access_right === action})
				.map((entity) => {
					return entity.id;
				});
		});
	}

	// TBD: write test for selecting
	// - all entities that are shared with a specific team with a specific right, etc.
	// - all entities that the user has 'own', 'write', 'connect' 'read' access to, etc.
	// - all entities that are have a specific public access right ('own', 'write', 'connect' 'read')
	// - that return the identity_id's instead of the entity ids,
	// since it might be more useful for some use cases,
	// such as sharing with teams, etc. (see the commented out code in the function for an example of how to do this)
	createAccessPolicyResourceSelection(
		name: string,
		policyFilterFn: (policy: AccessPolicy) => boolean,
		fromOtherSelection: string | undefined = undefined
	) {
		return this.createReactiveSelection(name, () => {
			this.#selections[name] = this.getSelectedEntities(fromOtherSelection)
				.filter((entity) => {
					const policies = this.accessPolicies[entity.id] || [];
					return policies.some(policyFilterFn);
				})
				.map((entity) => entity.id);
		});
	}

	createAccessPolicyIdentitySelection(
		name: string,
		policyFilterFn: (policy: AccessPolicy) => boolean,
		fromOtherSelection?: string
	) {
		this.addSelection(name);
		$effect(() => {
			const matchingIdentityIds = new SvelteSet(
				Object.values(this.accessPolicies)
					.flat()
					.filter(policyFilterFn)
					.map((policy) => policy.identity_id)
					.filter((id): id is string => Boolean(id))
			);

			this.#selections[name] = this.getSelectedIdentities(fromOtherSelection)
				.filter((identity) => matchingIdentityIds.has(identity.id))
				.map((identity) => identity.id);
		});
		return () => this.getSelectedIdentities(name);
	}

	createSortedSelection(
		name: string,
		attribute: keyof T,
		ascending = true,
		fromOtherSelection?: string
	) {
		return this.createReactiveSelection(name, () => {
			this.selections[name] = this.getSelectedEntities(fromOtherSelection)
				.toSorted((a, b) => {
					if (a[attribute] < b[attribute]) return ascending ? -1 : 1;
					if (a[attribute] > b[attribute]) return ascending ? 1 : -1;
					return 0;
				})
				.map((entity) => entity.id);
		});
	}
}
