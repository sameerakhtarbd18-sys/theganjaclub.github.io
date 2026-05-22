// Netlify Function: ask-grow
// Cannabis Cultivation Q&A — powered by DeepSeek + curated knowledge base
// Endpoint: POST /.netlify/functions/ask-grow

const DEEPSEEK_API_KEY = process.env.DEEPSEEK_API_KEY;

// Embedded knowledge base (trimmed for serverless — 3 documents, ~21K chars)
const KNOWLEDGE_BASE = require('./knowledge-base.json');

// Simple keyword-based retrieval
function searchKB(question) {
  const q = question.toLowerCase();
  const words = q.split(/\s+/).filter(w => w.length > 3);
  
  // Score each document by keyword overlap
  const scored = KNOWLEDGE_BASE.map(doc => {
    const content = doc.content.toLowerCase();
    let score = 0;
    for (const word of words) {
      const regex = new RegExp(word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
      const matches = content.match(regex);
      if (matches) score += matches.length;
    }
    return { ...doc, score };
  }).filter(d => d.score > 0).sort((a, b) => b.score - a.score);

  // Take top 2 documents, trim to fit context window
  return scored.slice(0, 2).map(d => ({
    source: d.source,
    excerpt: d.content.substring(0, 4000), // Limit per doc
    url: d.url
  }));
}

// Build system prompt with context
function buildPrompt(question, sources) {
  const context = sources.map((s, i) => 
    `[SOURCE ${i+1}: ${s.source}]\n${s.excerpt}\n[/SOURCE ${i+1}]`
  ).join('\n\n');

  return `You are "Grow Assistant", the cannabis cultivation expert for The Ganja Club — a UK medical cannabis media publication. You answer questions about growing cannabis for EDUCATIONAL PURPOSES ONLY. You never give medical advice, never encourage illegal activity, and always note that cultivation laws vary by jurisdiction.

Your tone: friendly, knowledgeable, British English. Like a helpful gardening expert who happens to specialise in cannabis. Use plain language. Cite the sources provided.

CRITICAL RULES:
- Never advise anyone to break UK law (cultivation without a Home Office licence is illegal in the UK)
- Never give medical advice or dosage recommendations
- Never describe consumption methods
- Always include the disclaimer when asked about health/medical topics
- If asked something outside cannabis cultivation, politely redirect

KNOWLEDGE BASE CONTEXT:
${context}

USER QUESTION: ${question}

Answer the question using the context above. If the context doesn't fully cover it, supplement with your general horticultural knowledge but make it clear when you're going beyond the provided sources. Keep answers under 300 words. Be specific and practical.`;
}

exports.handler = async (event) => {
  // CORS
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers };
  }

  if (event.httpMethod !== 'POST') {
    return { 
      statusCode: 405, 
      headers,
      body: JSON.stringify({ error: 'Method not allowed' }) 
    };
  }

  let body;
  try {
    body = JSON.parse(event.body);
  } catch {
    return { 
      statusCode: 400, 
      headers,
      body: JSON.stringify({ error: 'Invalid JSON' }) 
    };
  }

  const question = (body.question || '').trim();
  if (!question) {
    return { 
      statusCode: 400, 
      headers,
      body: JSON.stringify({ error: 'Question is required' }) 
    };
  }

  if (question.length > 500) {
    return {
      statusCode: 400,
      headers,
      body: JSON.stringify({ error: 'Question too long (max 500 characters)' })
    };
  }

  if (!DEEPSEEK_API_KEY) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: 'API key not configured' })
    };
  }

  try {
    // Search knowledge base
    const sources = searchKB(question);
    const prompt = buildPrompt(question, sources);

    // Call DeepSeek
    const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${DEEPSEEK_API_KEY}`
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [
          { role: 'system', content: prompt }
        ],
        temperature: 0.3,
        max_tokens: 600
      })
    });

    const data = await response.json();

    if (data.error) {
      console.error('DeepSeek API error:', data.error);
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ 
          error: 'AI service error', 
          detail: data.error.message 
        })
      };
    }

    const answer = data.choices?.[0]?.message?.content || 'Sorry, I could not generate an answer.';

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        answer,
        sources: sources.map(s => ({ source: s.source, url: s.url })),
        disclaimer: 'This information is for educational purposes only. It does not constitute medical or legal advice. Cultivation laws vary by jurisdiction — in the UK, cultivation of cannabis without a Home Office licence is illegal. Consult a qualified professional for personal advice.'
      })
    };

  } catch (error) {
    console.error('Function error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: 'Internal server error' })
    };
  }
};
