import { v4 } from 'uuid';
import { beforeEach, describe, expect, test } from 'vitest';

import { Action } from './accessHandler';
import { EntityContainer } from './entityContainer.svelte';

type AnyEntityExtended = {
	id: string;
	name: string;
	// other properties...
};

describe('EntityContainer', () => {
	let entityContainer: EntityContainer<AnyEntityExtended>;

	beforeEach(() => {
		$effect.root(() => {
			$effect(() => {
				entityContainer = new EntityContainer<AnyEntityExtended>();
			});
		});
	});

	test('should initialize with empty states', () => {
		expect(entityContainer.entities).toEqual([]);
		expect(entityContainer.pendingEntities).toEqual([]);
		expect(entityContainer.identities).toEqual([]);
		expect(entityContainer.accessPolicies).toEqual({});
		expect(entityContainer.accessRights).toEqual({});
		expect(entityContainer.hierarchies).toEqual({});
		expect(entityContainer.selections).toEqual({});
	});

	test('should getters and setters for all properties', () => {
		// Entities:
		const entity = { id: v4(), name: 'Test Entity' };
		entityContainer.entities = [entity];
		expect(entityContainer.entities).toEqual([entity]);
		entityContainer.entities = [];
		expect(entityContainer.entities).toEqual([]);
		// Pending Entities:
		const pendingEntity = { id: v4(), name: 'Pending Entity' };
		entityContainer.pendingEntities = [pendingEntity];
		expect(entityContainer.pendingEntities).toEqual([pendingEntity]);
		entityContainer.pendingEntities = [];
		expect(entityContainer.pendingEntities).toEqual([]);
		// Identities:
		const identity = { id: v4(), name: 'Test Identity' };
		entityContainer.identities = [identity];
		expect(entityContainer.identities).toEqual([identity]);
		entityContainer.identities = [];
		expect(entityContainer.identities).toEqual([]);
		// Access Policies:
		const accessPolicy = {
			resource_id: v4(),
			identity_id: v4(),
			action: Action.READ,
			public: false
		};
		const accessPolicyKey = v4();
		entityContainer.accessPolicies = { [accessPolicyKey]: [accessPolicy] };
		expect(entityContainer.accessPolicies).toEqual({ [accessPolicyKey]: [accessPolicy] });
		entityContainer.accessPolicies = {};
		expect(entityContainer.accessPolicies).toEqual({});
		const publicAccessPolicy = {
			resource_id: v4(),
			action: Action.READ,
			public: true,
			public_action: Action.WRITE
		};
		const publicAccessPolicyKey = v4();
		entityContainer.accessPolicies = { [publicAccessPolicyKey]: [publicAccessPolicy] };
		expect(entityContainer.accessPolicies).toEqual({
			[publicAccessPolicyKey]: [publicAccessPolicy]
		});
		entityContainer.accessPolicies = {};
		expect(entityContainer.accessPolicies).toEqual({});
		// Access Rights:
		const accessRight = { [v4()]: Action.READ };
		entityContainer.accessRights = accessRight;
		expect(entityContainer.accessRights).toEqual(accessRight);
		entityContainer.accessRights = {};
		expect(entityContainer.accessRights).toEqual({});
		const hierarchy = { child_id: v4(), parent_id: v4() };
		entityContainer.hierarchies = { '1': { children: [hierarchy] } };
		expect(entityContainer.hierarchies).toEqual({ '1': { children: [hierarchy] } });
		entityContainer.hierarchies = {};
		expect(entityContainer.hierarchies).toEqual({});
		const otherHierarchy = { child_id: v4(), parent_id: v4(), inherit: true, order: 1 };
		entityContainer.hierarchies = { '1': { parents: [otherHierarchy] } };
		expect(entityContainer.hierarchies).toEqual({ '1': { parents: [otherHierarchy] } });
		entityContainer.hierarchies = {};
		expect(entityContainer.hierarchies).toEqual({});
		// Selections:
		const selection = [v4()];
		entityContainer.selections = { testSelection: selection };
		expect(entityContainer.selections).toEqual({ testSelection: selection });
		entityContainer.selections = {};
		expect(entityContainer.selections).toEqual({});
	});

	test('should manage pending entities', () => {
		const pendingEntity = { name: 'Pending Entity' };
		entityContainer.createPending(pendingEntity);
		expect(entityContainer.pendingEntities.map((e) => e.name)).toContain(pendingEntity.name);
		const begining_of_id = entityContainer.pendingEntities[0].id.split('_')[0];
		expect(begining_of_id).toBe('new');
		entityContainer.pendingEntities = [];
		expect(entityContainer.pendingEntities).toEqual([]);
	});

	test('should manage selections', () => {
		const entity1 = { id: v4(), name: 'Entity 1' };
		const entity2 = { id: v4(), name: 'Entity 2' };
		entityContainer.entities = [entity1, entity2];
		entityContainer.addSelection('testSelection', [entity1.id]);
		expect(entityContainer.getSelectedEntities('testSelection')).toEqual([entity1]);
		entityContainer.addToSelection('testSelection', [entity2.id]);
		expect(entityContainer.getSelectedEntities('testSelection')).toEqual([entity1, entity2]);
		entityContainer.removeFromSelection('testSelection', [entity1.id]);
		expect(entityContainer.getSelectedEntities('testSelection')).toEqual([entity2]);
		entityContainer.removeSelection('testSelection');
		expect(entityContainer.selections).toEqual({});
	});
});
