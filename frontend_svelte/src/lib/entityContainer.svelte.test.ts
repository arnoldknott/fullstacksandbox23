import { flushSync } from 'svelte';
import { v4 } from 'uuid';
import { beforeEach, describe, expect, test } from 'vitest';

import { Action } from './accessHandler';
import { EntityContainer } from './entityContainer.svelte';

type AnyEntityExtended = {
	id: string;
	name: string;
	creation_date?: Date;
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

	test('should create filtered entity selection', () => {
		const entity1 = { id: v4(), name: 'Entity 1' };
		const entity2 = { id: v4(), name: 'Entity 2' };
		const entity3 = { id: v4(), name: 'Something else 3' };
		const entity4 = { id: v4(), name: 'Entity 4' };
		entityContainer.entities = [entity1, entity2, entity3, entity4];
		$effect.root(() => {
			entityContainer.createFilteredEntitySelection(
				'filteredSelection',
				(e) => e.name.slice(0, 6) === 'Entity'
			);
			entityContainer.createFilteredEntitySelection(
				'invertedFilteredSelection',
				(e) => e.name.slice(0, 6) !== 'Entity'
			);
		});
		flushSync();
		expect(entityContainer.getSelectedEntities('filteredSelection')).toEqual([
			entity1,
			entity2,
			entity4
		]);
		expect(entityContainer.getSelectedEntities('invertedFilteredSelection')).toEqual([entity3]);
	});

	// test('should create all linked selection', () => {
	// 	const entity1 = { id: v4(), name: 'Entity 1' };
	// 	const entity2 = { id: v4(), name: 'Entity 2' };
	// 	const entity3 = { id: v4(), name: 'Entity 3' };
	// 	const entity4 = { id: v4(), name: 'Entity 4' };
	// 	entityContainer.entities = [entity1, entity2, entity3, entity4];
	// 	const hierarchy12 = { child_id: entity2.id, parent_id: entity1.id };
	// 	const hierarchy13 = { child_id: entity3.id, parent_id: entity1.id };
	// 	const hierarchy24 = { child_id: entity4.id, parent_id: entity2.id };
	// 	entityContainer.hierarchies = {
	// 		[entity1.id]: { parents: [hierarchy12, hierarchy13] },
	// 		[entity2.id]: { children: [hierarchy12], parents: [hierarchy24] },
	// 		[entity3.id]: { children: [hierarchy13] },
	// 		[entity4.id]: { children: [hierarchy24] }
	// 	};
	// 	$effect.root(() => {
	// 		entityContainer.createLinkedSelection('linkedToEntity1', entity1.id);
	// 		entityContainer.createLinkedSelection('linkedToEntity2', entity2.id);
	// 		entityContainer.createLinkedSelection('linkedToEntity1Inverted', entity1.id, true);
	// 	});
	// 	flushSync(() => {});
	// 	expect(entityContainer.getSelectedEntities('linkedToEntity1')).toEqual([entity2, entity3]);
	// 	expect(entityContainer.getSelectedEntities('linkedToEntity2')).toEqual([entity1, entity4]);
	// 	expect(entityContainer.getSelectedEntities('linkedToEntity1Inverted')).toEqual([entity4]);
	// });

	test('should create user has specific access right selection', () => {
		const entity1 = { id: v4(), name: 'Entity 1' };
		const entity2 = { id: v4(), name: 'Entity 2' };
		const entity3 = { id: v4(), name: 'Entity 3' };
		const entity4 = { id: v4(), name: 'Entity 4' };
		entityContainer.entities = [entity1, entity2, entity3, entity4];
		const accessRight1 = { [entity1.id]: Action.OWN };
		const accessRight2 = { [entity2.id]: Action.WRITE };
		const accessRight3 = { [entity3.id]: Action.CONNECT };
		const accessRight4 = { [entity4.id]: Action.READ };
		entityContainer.accessRights = {
			...accessRight1,
			...accessRight2,
			...accessRight3,
			...accessRight4
		};
		$effect.root(() => {
			entityContainer.createUserHasSpecificAccessRightSelection('ownSelection', Action.OWN);
			entityContainer.createUserHasSpecificAccessRightSelection('writeSelection', Action.WRITE);
			entityContainer.createUserHasSpecificAccessRightSelection('connectSelection', Action.CONNECT);
			entityContainer.createUserHasSpecificAccessRightSelection('readSelection', Action.READ);
		});
		flushSync();
		expect(entityContainer.getSelectedEntities('ownSelection')).toEqual([entity1]);
		expect(entityContainer.getSelectedEntities('writeSelection')).toEqual([entity2]);
		expect(entityContainer.getSelectedEntities('connectSelection')).toEqual([entity3]);
		expect(entityContainer.getSelectedEntities('readSelection')).toEqual([entity4]);
	});

	// test('should create access policy resource selection', () => {
	// 	const entity1 = { id: v4(), name: 'Entity 1' };
	// 	const entity2 = { id: v4(), name: 'Entity 2' };
	// 	const entity3 = { id: v4(), name: 'Entity 3' };
	// 	const entity4 = { id: v4(), name: 'Entity 4' };
	// 	entityContainer.entities = [entity1, entity2, entity3, entity4];
	// 	const accessPolicy1 = { resource_id: entity1.id, action: Action.READ, public: false };
	// 	const accessPolicy2 = { resource_id: entity2.id, action: Action.WRITE, public: false };
	// 	const accessPolicy3 = { resource_id: entity3.id, action: Action.CONNECT, public: false };
	// 	const accessPolicy4 = { resource_id: entity4.id, action: Action.READ, public: false };
	// 	const accessPolicyKey1 = v4();
	// 	const accessPolicyKey2 = v4();
	// 	const accessPolicyKey3 = v4();
	// 	const accessPolicyKey4 = v4();
	// 	entityContainer.accessPolicies = {
	// 		[accessPolicyKey1]: [accessPolicy1],
	// 		[accessPolicyKey2]: [accessPolicy2],
	// 		[accessPolicyKey3]: [accessPolicy3],
	// 		[accessPolicyKey4]: [accessPolicy4]
	// 	};
	// 	$effect.root(() => {
	// 		entityContainer.createAccessPolicyResourceSelection(
	// 			'readResources',
	// 			(policy) => policy.action === Action.READ
	// 		);
	// 		entityContainer.createAccessPolicyResourceSelection(
	// 			'writeResources',
	// 			(policy) => policy.action === Action.WRITE
	// 		);
	// 	});
	//     flushSync();
	// 	expect(entityContainer.getSelectedEntities('readResources')).toEqual([entity1, entity4]);
	// 	expect(entityContainer.getSelectedEntities('writeResources')).toEqual([entity2]);
	// });

	// test('should create access policy identity selection', () => {
	// 	const entity1 = { id: v4(), name: 'Entity 1' };
	// 	const entity2 = { id: v4(), name: 'Entity 2' };
	// 	const entity3 = { id: v4(), name: 'Entity 3' };
	// 	const entity4 = { id: v4(), name: 'Entity 4' };
	// 	entityContainer.entities = [entity1, entity2, entity3, entity4];
	// 	const identity1 = { id: v4(), name: 'Identity 1' };
	// 	const identity2 = { id: v4(), name: 'Identity 2' };
	// 	const identity3 = { id: v4(), name: 'Identity 3' };
	// 	const identity4 = { id: v4(), name: 'Identity 4' };
	// 	entityContainer.identities = [identity1, identity2, identity3, identity4];
	// 	const accessPolicy1 = {
	// 		resource_id: entity1.id,
	// 		identity_id: identity1.id,
	// 		action: Action.READ,
	// 		public: false
	// 	};
	// 	const accessPolicy2 = {
	// 		resource_id: entity2.id,
	// 		identity_id: identity2.id,
	// 		action: Action.WRITE,
	// 		public: false
	// 	};
	// 	const accessPolicy3 = {
	// 		resource_id: entity3.id,
	// 		identity_id: identity3.id,
	// 		action: Action.CONNECT,
	// 		public: false
	// 	};
	// 	const accessPolicy4 = {
	// 		resource_id: entity4.id,
	// 		identity_id: identity4.id,
	// 		action: Action.READ,
	// 		public: false
	// 	};
	// 	const accessPolicyKey1 = v4();
	// 	const accessPolicyKey2 = v4();
	// 	const accessPolicyKey3 = v4();
	// 	const accessPolicyKey4 = v4();
	// 	entityContainer.accessPolicies = {
	// 		[accessPolicyKey1]: [accessPolicy1],
	// 		[accessPolicyKey2]: [accessPolicy2],
	// 		[accessPolicyKey3]: [accessPolicy3],
	// 		[accessPolicyKey4]: [accessPolicy4]
	// 	};
	// 	$effect.root(() => {
	// 		entityContainer.createAccessPolicyIdentitySelection(
	// 			'identity1Resources',
	// 			(policy) => policy.identity_id === identity1.id
	// 		);
	// 		entityContainer.createAccessPolicyIdentitySelection(
	// 			'identity2Resources',
	// 			(policy) => policy.identity_id === identity2.id
	// 		);
	// 		entityContainer.createAccessPolicyIdentitySelection(
	// 			'identity3Resources',
	// 			(policy) => policy.identity_id === identity3.id
	// 		);
	// 		entityContainer.createAccessPolicyIdentitySelection(
	// 			'identity4Resources',
	// 			(policy) => policy.identity_id === identity4.id
	// 		);
	// 	});
	//     flushSync();
	// 	expect(entityContainer.getSelectedEntities('identity1Resources')).toEqual([entity1]);
	// 	expect(entityContainer.getSelectedEntities('identity2Resources')).toEqual([entity2]);
	// 	expect(entityContainer.getSelectedEntities('identity3Resources')).toEqual([entity3]);
	// 	expect(entityContainer.getSelectedEntities('identity4Resources')).toEqual([entity4]);
	// });

	test('should create sorted selection', () => {
		const entity1 = { id: v4(), name: 'Entity 1', creation_date: '2024-01-01' };
		const entity2 = { id: v4(), name: 'Entity 2', creation_date: '2024-03-01' };
		const entity3 = { id: v4(), name: 'Entity 3', creation_date: '2024-02-01' };
		const entity4 = { id: v4(), name: 'Entity 4' };
		entityContainer.entities = [entity1, entity2, entity3, entity4];
		$effect.root(() => {
			entityContainer.createSortedSelection('sortedByCreationDate', 'creation_date');
			entityContainer.createSortedSelection('sortedByCreationDateDesc', 'creation_date', false);
		});
		flushSync();
		expect(entityContainer.getSelectedEntities('sortedByCreationDate')).toEqual([
			entity1,
			entity3,
			entity2,
			entity4
		]);
		expect(entityContainer.getSelectedEntities('sortedByCreationDateDesc')).toEqual([
			entity2,
			entity3,
			entity1,
			entity4
		]);
	});

	test('should throw error when creating all linked selection without parentId', () => {
		$effect.root(() => {
			expect(() =>
				entityContainer.createLinkedSelection('test', undefined as unknown as string)
			).toThrowError(
				"Parent ID must be provided either as an argument or as the EntityContainer's parentId property."
			);
		});
	});
});
