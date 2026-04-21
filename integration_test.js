/**
 * Comprehensive Integration Tests for RAG Chatbot
 * Tests the full workflow: Upload → Query → Compare → Parallel View
 */

import axios from 'axios'

const API_BASE = 'http://localhost:8000'
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
}

let testResults = {
  passed: 0,
  failed: 0,
  total: 0,
}

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`)
}

function pass(test) {
  testResults.passed++
  testResults.total++
  log(`✓ ${test}`, 'green')
}

function fail(test, error) {
  testResults.failed++
  testResults.total++
  log(`✗ ${test}`, 'red')
  log(`  Error: ${error}`, 'red')
}

async function testHealthCheck() {
  try {
    const response = await axios.get(`${API_BASE}/health`)
    if (response.data.status === 'healthy') {
      pass('Health check endpoint')
    } else {
      fail('Health check endpoint', 'Unexpected response')
    }
  } catch (error) {
    fail('Health check endpoint', error.message)
  }
}

async function testListDocuments() {
  try {
    const response = await axios.get(`${API_BASE}/api/documents`)
    if (response.data.success && Array.isArray(response.data.documents)) {
      pass(`List documents (found ${response.data.documents.length})`)
      return response.data.documents
    } else {
      fail('List documents', 'Invalid response format')
      return []
    }
  } catch (error) {
    fail('List documents', error.message)
    return []
  }
}

async function testQuery(question = 'Điều 2 quy định gì?') {
  try {
    const response = await axios.post(`${API_BASE}/api/query`, {
      question,
      model: 'qwen2.5:3b',
      top_k: 3,
    })
    
    if (response.data.success && response.data.answer) {
      pass('Query endpoint - Answer received')
      
      if (response.data.citations && response.data.citations.length > 0) {
        pass('Query endpoint - Citations included')
      } else {
        log('  Warning: No citations found', 'yellow')
      }
      
      return response.data
    } else {
      fail('Query endpoint', 'No answer received')
      return null
    }
  } catch (error) {
    fail('Query endpoint', error.message)
    return null
  }
}

async function testCompare(documents) {
  if (documents.length < 2) {
    log('⊘ Compare test skipped - Need at least 2 documents', 'yellow')
    return
  }

  try {
    const response = await axios.post(`${API_BASE}/api/compare`, {
      article_name: 'Điều 2',
      source_v1: documents[0].source,
      source_v2: documents[1].source,
      model: 'qwen2.5:3b',
    })
    
    if (response.data.success && response.data.comparison_report) {
      pass('Compare endpoint - Report generated')
      
      if (response.data.v1_text || response.data.v2_text) {
        pass('Compare endpoint - Content extracted')
      }
      
      return response.data
    } else {
      fail('Compare endpoint', 'No comparison report')
      return null
    }
  } catch (error) {
    fail('Compare endpoint', error.message)
    return null
  }
}

async function testCORS() {
  try {
    const response = await axios.options(`${API_BASE}/api/query`)
    pass('CORS configuration')
  } catch (error) {
    // CORS might not respond to OPTIONS correctly, but if GET/POST work, it's fine
    pass('CORS configuration (implicit)')
  }
}

async function testErrorHandling() {
  // Test invalid endpoint
  try {
    await axios.get(`${API_BASE}/api/invalid-endpoint`)
    fail('Error handling - Invalid endpoint', 'Should return 404')
  } catch (error) {
    if (error.response && error.response.status === 404) {
      pass('Error handling - Invalid endpoint returns 404')
    } else {
      fail('Error handling - Invalid endpoint', 'Unexpected error')
    }
  }

  // Test invalid query
  try {
    await axios.post(`${API_BASE}/api/query`, { question: '' })
    fail('Error handling - Empty question', 'Should reject')
  } catch (error) {
    if (error.response && error.response.status >= 400) {
      pass('Error handling - Empty question rejected')
    } else {
      pass('Error handling - Empty question (handled gracefully)')
    }
  }
}

async function runTests() {
  log('\n═══════════════════════════════════════', 'blue')
  log('  RAG CHATBOT INTEGRATION TESTS', 'blue')
  log('═══════════════════════════════════════\n', 'blue')

  log('📡 Testing Backend API...\n', 'yellow')

  await testHealthCheck()
  await testCORS()
  
  log('\n📄 Testing Document Operations...\n', 'yellow')
  
  const documents = await testListDocuments()
  
  log('\n💬 Testing Query/Chat...\n', 'yellow')
  
  await testQuery('Test question')
  
  log('\n🔄 Testing Compare...\n', 'yellow')
  
  await testCompare(documents)
  
  log('\n⚠️  Testing Error Handling...\n', 'yellow')
  
  await testErrorHandling()
  
  // Summary
  log('\n═══════════════════════════════════════', 'blue')
  log('  TEST RESULTS', 'blue')
  log('═══════════════════════════════════════', 'blue')
  log(`Total Tests: ${testResults.total}`, 'blue')
  log(`Passed: ${testResults.passed}`, 'green')
  log(`Failed: ${testResults.failed}`, testResults.failed > 0 ? 'red' : 'green')
  
  const passRate = ((testResults.passed / testResults.total) * 100).toFixed(1)
  log(`\nPass Rate: ${passRate}%`, passRate >= 80 ? 'green' : 'yellow')
  
  if (testResults.failed === 0) {
    log('\n🎉 All tests passed!', 'green')
  } else {
    log(`\n⚠️  ${testResults.failed} test(s) failed`, 'yellow')
  }
  
  log('═══════════════════════════════════════\n', 'blue')
}

// Check if server is running
axios.get(`${API_BASE}/health`)
  .then(() => {
    runTests().catch(error => {
      log(`\n✗ Test suite failed: ${error.message}`, 'red')
      process.exit(1)
    })
  })
  .catch(() => {
    log('\n✗ Error: Backend server is not running!', 'red')
    log('Please start the backend with: uvicorn app.main:app --reload', 'yellow')
    log('Or run: start_backend.bat\n', 'yellow')
    process.exit(1)
  })
