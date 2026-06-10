import { Action } from './accessHandler';
import type { AccessPolicy, AnyEntityExtended, Hierarchy } from './types';

/**
 * Functions that provide the Data for class EntityContainer to manage. Evaluated inside a
 * `$effect`, so it runs once on construction (seeding the internal entities array) and
 * then re-runs whenever any reactive value it reads changes — typically `data.*` from
 * SvelteKit's PageData after navigation, `invalidate`, or form actions.
 */
type EntityData<T> = {
	seedEntities?: () => T[];
	seedPendingEntities?: () => T[];
	seedAccessPolicies?: () => Record<string, AccessPolicy[]>;
	seedAccessRights?: () => Record<string, Action>;
	seedHierarchies?: () => Hierarchy[];
	seedSelections?: () => Record<string, string[]>;
	parentId?: string; // should it be here?
};

/**
 * For managing new entities before submitting them,
 * they are alive in the frontend only and EntityContainer holds space for them.
 */
type PendingConfiguration<T extends AnyEntityExtended = AnyEntityExtended> = {
	// parentId?: string; // should it be here?
	inherit?: boolean;
	public?: boolean;
	publicAction?: Action;
	template?: Partial<Omit<T, 'id'>>;
};

export type EntityContainerConfiguration<T extends AnyEntityExtended = AnyEntityExtended> = Partial<
	EntityData<T> & PendingConfiguration<T>
>;

export interface EntityContainerInterface<T extends AnyEntityExtended = AnyEntityExtended> {
	entities: T[];
	pendingEntities: T[];
	accessPolicies: Record<string, AccessPolicy[]>;
	accessRights: Record<string, Action>;
	hierarchies: Hierarchy[];
	selections: Record<string, string[]>;
	parentId?: string | null;
	// defaultInherit: boolean;
	// defaultPublic: boolean;
	// defaultPublicAction: Action;
	pendingTemplate?: Partial<Omit<T, 'id'>>;
	pendingSubmitOptions?: {
		parentId?: string;
		inherit?: boolean;
		public?: boolean;
		publicAction?: Action;
	};
	createPending(overrides?: Partial<T>): T;
	addSelection(name: string, entityIds: string[]): string[];
	getSelectedEntities(name: string): T[];
	addToSelection(name: string, entityIds: string[]): string[];
	removeFromSelection(name: string, entityIds: string[]): string[];
	createFilteredSelection(name: string, filterFn: (entity: T) => boolean): T[];
	createAllLinkedSelection(
		name: string,
		parentId: string,
		initialIds?: string[],
		inverse?: boolean
	): T[];
	sortSelectionBy(name: string, attribute: keyof T, ascending?: boolean): void;
}

export class EntityContainer<
	T extends AnyEntityExtended = AnyEntityExtended
> implements EntityContainerInterface<T> {
	#entities = $state<T[]>([]); // AnyEntityExtended[];
	#pendingEntities = $state<T[]>([]); // AnyEntityExtended[];
	#accessPolicies = $state<Record<string, AccessPolicy[]>>({}); // UUID: AccessPolicy[]
	#accessRights = $state<Record<string, Action>>({}); // UUID: Action
	#hierarchies = $state<Hierarchy[]>([]); // flat array of all hierarchies
	#selections = $state<Record<string, string[]>>({}); // selectionName: entityIds[]
	parentId?: string | null;
	// defaultInherit: boolean = false;
	// defaultPublic: boolean = false;
	// defaultPublicAction: Action = Action.READ;
	pendingTemplate?: Partial<Omit<T, 'id'>>; // AnyEntityExtended without id;
	pendingSubmitOptions?: {
		parentId?: string;
		inherit?: boolean;
		public?: boolean;
		publicAction?: Action;
	};

	constructor(configuration: EntityContainerConfiguration<T> = {}) {
		// TBD: do we need a function to seed the data (and first time use it here)
		// for re-seeding or is it enough to do this through the setter?
		$effect(() => {
			this.#entities = configuration.seedEntities ? configuration.seedEntities() : [];
			this.#pendingEntities = configuration.seedPendingEntities
				? configuration.seedPendingEntities()
				: [];
			this.#accessPolicies = configuration.seedAccessPolicies
				? configuration.seedAccessPolicies()
				: {};
			this.#accessRights = configuration.seedAccessRights ? configuration.seedAccessRights() : {};
			this.#hierarchies = configuration.seedHierarchies ? configuration.seedHierarchies() : [];
			this.#selections = configuration.seedSelections ? configuration.seedSelections() : {};
		});
		this.parentId = configuration.parentId ?? undefined;
		this.pendingTemplate = configuration.template ?? undefined; // TBD: change into setting all values, but the id value to null/undifned/empty, whatver is adequate - note the mandartory keys!
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

	get hierarchies(): Hierarchy[] {
		return this.#hierarchies;
	}
	set hierarchies(value: Hierarchy[]) {
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
	 * swaps for a real UUID on `status:created`, at which point {@link handleStatus}
	 * rewrites it in place). Merges, in order: the configured `pendingTemplate` (if any),
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

	// TBD: consider moving the Selection in its own class and here?

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
	addSelection(name: string, entityIds: string[]) {
		if (this.#selections[name]) {
			throw new Error(`Selection with name "${name}" already exists.`);
		}
		this.#selections[name] = entityIds;
		return this.#selections[name];
	}

	// getSelection(name: string) {
	//     if (!this.#selections[name]) {
	//         throw new Error(`Selection with name "${name}" does not exist.`);
	//     }
	//     return this.#selections[name];
	// }

	/**
	 * Gets all entities that match this specific selection with its assigned selection function
	 *
	 * Call with $derived.by(() => entityContainer.getSelectedEntities('mySelection'))
	 * in caller to reactively get the selected entities for this selection.
	 * @param name specifies which selection to retrieve
	 * @returns the entities that correlate to the specified selection
	 */
	getSelectedEntities(name: string) {
		// return $derived.by(() => {
		const selectedIds = this.selections[name];
		return this.entities.filter((entity) => selectedIds.includes(entity.id));
		// });
	}

	addToSelection(name: string, entityIds: string[]) {
		if (!this.#selections[name]) {
			throw new Error(`Selection with name "${name}" does not exist.`);
		}
		this.#selections[name] = [...this.#selections[name], ...entityIds];
		return this.#selections[name];
	}

	removeFromSelection(name: string, entityIds: string[]) {
		if (!this.#selections[name]) {
			throw new Error(`Selection with name "${name}" does not exist.`);
		}
		this.#selections[name] = this.#selections[name].filter((id) => !entityIds.includes(id));
		return this.#selections[name];
	}

	// for example all entities that match a specific condition
	// TBD: extend with choosing different data containers, such as
	// accessPolicies, hierarchies, etc. for more complex selection logic,
	// e.g. select all entities that are shared with a specific team with a specific right,
	/**
	 *
	 * @param name
	 * @param filterFn
	 * @param initialIds
	 * @returns
	 *
	 * see also {@link createAllLinkedSelection}
	 */
	createFilteredSelection(
		name: string,
		filterFn: (entity: T) => boolean,
		initialIds: string[] = []
	) {
		this.addSelection(name, initialIds);
		$effect(() => {
			this.#selections[name] = this.entities.filter(filterFn).map((entity) => entity.id);
		});
		// return this.#selections[name];// TBD: is this even necessary?
		return $derived.by(() => this.getSelectedEntities(name));
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
	 */
	createAllLinkedSelection(
		name: string,
		parentId?: string,
		initialIds: string[] = [],
		inverse: boolean = false
	) {
		this.addSelection(name, initialIds);
		$effect(() => {
			const parentIdToUse = parentId ?? this.parentId;
			if (!parentIdToUse) {
				throw new Error(
					"Parent ID must be provided either as an argument or as the EntityContainer's parentId property."
				);
			}
			this.#selections[name] =
				this.#hierarchies
					.filter((hierarchy) => {
						if (!inverse) return hierarchy.parent_id === parentIdToUse;
						else return hierarchy.parent_id !== parentIdToUse;
					})
					.map((hierarchy) => hierarchy.child_id) || [];
		});
		return $derived.by(() => this.getSelectedEntities(name));
	}

	createUserHasSpecificAccessRightSelection(
		name: string,
		action: Action,
		initialIds: string[] = []
	) {
		this.addSelection(name, initialIds);
		$effect(() => {
			this.#selections[name] = this.entities
				.filter((entity) => this.accessRights[entity.id] === action)
				.map((entity) => entity.id);
		});
		return $derived.by(() => this.getSelectedEntities(name));
	}

	// TBD: write test for selecting
	// - all entities that are shared with a specific team with a specific right, etc.
	// - all entities that the user has 'own', 'write', 'connect' 'read' access to, etc.
	// - all entities that are have a specific public access right ('own', 'write', 'connect' 'read')
	// - that return the identity_id's instead of the entity ids,
	// since it might be more useful for some use cases,
	// such as sharing with teams, etc. (see the commented out code in the function for an example of how to do this)
	// createAccessPolicyBasedSelection(name: string, policyFilterFn: (policy: AccessPolicy) => boolean, initialIds: string[] = [], identityReturn?: boolean = false) {
	//     this.addSelection(name, initialIds);
	//     $effect(() => {
	//         this.#selections[name] = this.entities
	//         .filter((entity) => {
	//             const policies = this.accessPolicies[entity.id] || [];
	//             return policies.some(policyFilterFn);
	//         })
	//         .map(
	//             (entity) => {
	//                 if(!identityReturn) return entity.id;
	//                 else return entity.access_policies?.map((policy) => policy.identity_id) || []; // TBD: is this the right way to handle this? should we return an empty array if there is no identity_id or should we filter out these entities? should we throw an error if there is no identity_id, since it might be a sign of misconfigured access policies?
	//             }
	//         );
	//     });
	//     return $derived.by(() => this.getSelectedEntities(name));
	// }

	sortSelectionBy(name: string, attribute: keyof T, ascending = true) {
		this.entities.sort((a, b) => {
			if (a[attribute] < b[attribute]) return ascending ? -1 : 1;
			if (a[attribute] > b[attribute]) return ascending ? 1 : -1;
			return 0;
		});
		this.#selections[name] = this.getSelectedEntities(name).map((entity) => entity.id);
	}
}
