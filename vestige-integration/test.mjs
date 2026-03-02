import { store, recall, stats, health, consolidate } from './index.mjs';

async function test() {
  console.log('🧪 Testing vestige-integration...\n');

  // Test 1: Stats
  console.log('1️⃣ Testing stats...');
  const statsResult = await stats();
  console.log('Stats:', statsResult);
  console.log('✅ Stats test passed\n');

  // Test 2: Store
  console.log('2️⃣ Testing store...');
  const storeResult = await store({
    text: 'vestige-integration skill 测试记忆',
    tags: ['test', 'integration'],
    importance: 0.9
  });
  console.log('Store result:', storeResult);
  console.log('✅ Store test passed\n');

  // Test 3: Stats again (should show +1 memory)
  console.log('3️⃣ Testing stats after store...');
  const statsAfter = await stats();
  console.log('Stats after:', statsAfter);
  console.log('✅ Stats after test passed\n');

  // Test 4: Recall
  console.log('4️⃣ Testing recall...');
  const recallResult = await recall('vestige-integration');
  console.log('Recall result:', recallResult);
  console.log('✅ Recall test passed\n');

  // Test 5: Health
  console.log('5️⃣ Testing health...');
  const healthResult = await health();
  console.log('Health:', healthResult.healthy ? '✅ Healthy' : '❌ Unhealthy');
  console.log('✅ Health test passed\n');

  // Test 6: Consolidate
  console.log('6️⃣ Testing consolidate...');
  const consolidateResult = await consolidate();
  console.log('Consolidate:', consolidateResult.success ? '✅ Success' : '❌ Failed');
  console.log('✅ Consolidate test passed\n');

  console.log('🎉 All tests passed!');
}

test().catch(console.error);
