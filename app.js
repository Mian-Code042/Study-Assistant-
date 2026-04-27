// API Configuration
const API_URL = 'http://localhost:8000';

// State
let documentProcessed = false;
let chatHistory = [];
let questionsAsked = 0;

// Initialize
$(document).ready(function() {
    initializeEventListeners();
    updateStats();
});

// Event Listeners
function initializeEventListeners() {
    // File Upload
    $('#pdfUpload').on('change', handleFileSelect);
    $('#processBtn').on('click', processDocument);
    
    // Tabs
    $('.tab-btn').on('click', function() {
        const tab = $(this).data('tab');
        switchTab(tab);
    });
    
    // Ask Questions
    $('#askBtn').on('click', askQuestion);
    $('#questionInput').on('keypress', function(e) {
        if (e.which === 13) askQuestion();
    });
    
    // MCQ
    $('#generateMcqBtn').on('click', generateMCQ);
    
    // Flashcards
    $('#generateFlashcardsBtn').on('click', generateFlashcards);
}

// File Handling
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
        $('#fileNameText').text(file.name);
        $('#fileName').removeClass('hidden').addClass('fade-in');
        $('#processBtn').removeClass('hidden').addClass('fade-in');
    }
}

async function processDocument() {
    const fileInput = document.getElementById('pdfUpload');
    const file = fileInput.files[0];
    
    if (!file) {
        showNotification('Please select a PDF file', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    showLoading('Processing PDF...');
    
    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            documentProcessed = true;
            updateDocumentStatus(file.name, true);
            showNotification('Document processed successfully!', 'success');
        } else {
            throw new Error('Processing failed');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to process document. Is the backend running?', 'error');
    } finally {
        hideLoading();
    }
}

// Tab Switching
function switchTab(tabName) {
    // Update tab buttons
    $('.tab-btn').removeClass('tab-active').addClass('text-gray-400');
    $(`.tab-btn[data-tab="${tabName}"]`).addClass('tab-active').removeClass('text-gray-400');
    
    // Update tab content
    $('.tab-content').addClass('hidden');
    $(`#${tabName}Tab`).removeClass('hidden').addClass('fade-in');
    
    // Load history when history tab is opened
    if (tabName === 'history') {
        loadHistory();
    }
}

// Ask Questions
async function askQuestion() {
    const question = $('#questionInput').val().trim();
    
    if (!question) {
        showNotification('Please enter a question', 'error');
        return;
    }
    
    if (!documentProcessed) {
        showNotification('Please upload and process a PDF first', 'error');
        return;
    }
    
    // Add user message
    addChatMessage(question, 'user');
    $('#questionInput').val('');
    $('#askEmpty').hide();
    
    showLoading('Thinking...');
    
    try {
        const response = await fetch(`${API_URL}/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });
        
        if (response.ok) {
            const data = await response.json();
            addChatMessage(data.answer, 'ai');
            questionsAsked++;
            updateStats();
        } else {
            throw new Error('Request failed');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to get answer. Check backend connection.', 'error');
    } finally {
        hideLoading();
    }
}

function addChatMessage(message, type) {
    const isUser = type === 'user';
    const messageHtml = `
        <div class="fade-in ${isUser ? 'ml-16' : 'mr-16'}">
            <div class="text-xs font-semibold uppercase tracking-wider mb-2 ${isUser ? 'text-right text-gray-500' : 'text-gold'}">
                ${isUser ? 'You' : 'StudyMind'}
            </div>
            <div class="bg-${isUser ? 'dark-light border border-gray-800' : 'gold/10 border border-gold/20'} rounded-2xl p-4 ${isUser ? 'rounded-tr-sm' : 'rounded-tl-sm'}">
                <p class="text-${isUser ? 'gray-300' : 'gray-200'} leading-relaxed">${escapeHtml(message)}</p>
            </div>
        </div>
    `;
    $('#chatHistory').append(messageHtml);
    $('#chatHistory')[0].scrollTop = $('#chatHistory')[0].scrollHeight;
}

// Generate MCQ
async function generateMCQ() {
    const topic = $('#mcqTopic').val().trim();
    const count = parseInt($('#mcqCount').val());
    
    if (!topic) {
        showNotification('Please enter a topic', 'error');
        return;
    }
    
    if (!documentProcessed) {
        showNotification('Please upload and process a PDF first', 'error');
        return;
    }
    
    $('#mcqEmpty').hide();
    showLoading(`Generating ${count} questions...`);
    
    try {
        const response = await fetch(`${API_URL}/mcqs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic, count })
        });
        
        if (response.ok) {
            const data = await response.json();
            displayMCQs(data.mcqs);
        } else {
            throw new Error('Request failed');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to generate MCQs', 'error');
    } finally {
        hideLoading();
    }
}

function displayMCQs(rawText) {
    const mcqs = parseMCQs(rawText);
    $('#mcqResults').empty();
    
    if (mcqs.length === 0) {
        $('#mcqResults').html(`<div class="bg-dark-light border border-gray-800 rounded-xl p-6 text-gray-300">${escapeHtml(rawText)}</div>`);
        return;
    }
    
    mcqs.forEach((mcq, index) => {
        const mcqHtml = `
            <div class="bg-dark-light border border-gray-800 rounded-2xl p-6 card-hover fade-in">
                <div class="text-xs font-bold uppercase tracking-wider text-gold mb-3">Question ${String(index + 1).padStart(2, '0')}</div>
                <h4 class="font-display text-lg font-semibold text-white mb-4">${escapeHtml(mcq.question)}</h4>
                <div class="space-y-2">
                    ${Object.entries(mcq.options).map(([letter, text]) => {
                        const isCorrect = letter === mcq.correct;
                        return `
                            <div class="flex items-center gap-3 p-3 rounded-xl border ${isCorrect ? 'bg-green-500/10 border-green-500/30' : 'bg-gray-800/30 border-gray-700'} transition-all hover:border-gold/50">
                                <span class="flex-shrink-0 w-8 h-8 rounded-lg ${isCorrect ? 'bg-green-500/20 border-green-500/40' : 'bg-gray-700/50 border-gray-600'} border flex items-center justify-center text-sm font-bold ${isCorrect ? 'text-green-400' : 'text-gray-400'}">${letter}</span>
                                <span class="text-gray-300">${escapeHtml(text)}</span>
                            </div>
                        `;
                    }).join('')}
                </div>
                ${mcq.correct ? `
                    <div class="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-500/10 border border-green-500/30 text-green-400 text-sm font-semibold">
                        <i class="fas fa-check-circle"></i>
                        Correct: ${mcq.correct} — ${escapeHtml(mcq.options[mcq.correct] || '')}
                    </div>
                ` : ''}
            </div>
        `;
        $('#mcqResults').append(mcqHtml);
    });
}

// Generate Flashcards
async function generateFlashcards() {
    const topic = $('#flashcardTopic').val().trim();
    const count = parseInt($('#flashcardCount').val());
    
    if (!topic) {
        showNotification('Please enter a topic', 'error');
        return;
    }
    
    if (!documentProcessed) {
        showNotification('Please upload and process a PDF first', 'error');
        return;
    }
    
    $('#flashcardsEmpty').hide();
    showLoading(`Creating ${count} flashcards...`);
    
    try {
        const response = await fetch(`${API_URL}/flashcards`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic, count })
        });
        
        if (response.ok) {
            const data = await response.json();
            displayFlashcards(data.flashcards);
        } else {
            throw new Error('Request failed');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to generate flashcards', 'error');
    } finally {
        hideLoading();
    }
}

function displayFlashcards(rawText) {
    const cards = parseFlashcards(rawText);
    $('#flashcardResults').empty();
    
    if (cards.length === 0) {
        $('#flashcardResults').html(`<div class="col-span-2 bg-dark-light border border-gray-800 rounded-xl p-6 text-gray-300">${escapeHtml(rawText)}</div>`);
        return;
    }
    
    cards.forEach((card, index) => {
        const cardHtml = `
            <div class="flashcard-container cursor-pointer fade-in" onclick="flipCard(this)">
                <div class="flashcard-inner">
                    <!-- Front -->
                    <div class="flashcard-front bg-dark-light border border-gray-800 rounded-2xl overflow-hidden">
                        <div class="absolute top-4 right-4 text-xs font-bold text-gold/50">#${String(index + 1).padStart(2, '0')}</div>
                        <div class="bg-gradient-to-br from-gold/10 to-gold/5 border-b border-gold/20 p-6 min-h-[150px] flex flex-col justify-center">
                            <div class="text-xs font-bold uppercase tracking-wider text-gold mb-3">◆ FRONT</div>
                            <p class="font-display text-lg font-semibold text-white leading-relaxed">${escapeHtml(card.front)}</p>
                            <div class="text-center text-xs text-gold/40 uppercase tracking-wider mt-4">Click to reveal</div>
                        </div>
                    </div>
                    
                    <!-- Back -->
                    <div class="flashcard-back bg-dark-light border border-gray-800 rounded-2xl overflow-hidden">
                        <div class="absolute top-4 right-4 text-xs font-bold text-gold/50">#${String(index + 1).padStart(2, '0')}</div>
                        <div class="bg-gradient-to-br from-green-500/10 to-green-500/5 border-b border-green-500/20 p-6 min-h-[150px] flex flex-col justify-center">
                            <div class="text-xs font-bold uppercase tracking-wider text-green-400 mb-3">◈ BACK</div>
                            <p class="text-gray-300 leading-relaxed">${escapeHtml(card.back)}</p>
                            <div class="text-center text-xs text-green-400/40 uppercase tracking-wider mt-4">Click to flip</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        $('#flashcardResults').append(cardHtml);
    });
}

function flipCard(element) {
    $(element).toggleClass('flipped');
}

// Load History
async function loadHistory() {
    showLoading('Loading history...');
    
    try {
        const response = await fetch(`${API_URL}/history?limit=50`);
        
        if (response.ok) {
            const data = await response.json();
            displayHistory(data.history);
        } else {
            throw new Error('Request failed');
        }
    } catch (error) {
        console.error('Error:', error);
        $('#historyResults').html(`
            <div class="text-center py-16 border-2 border-dashed border-gray-800 rounded-2xl">
                <div class="w-16 h-16 mx-auto mb-4 rounded-full border-2 border-red-500/30 bg-red-500/10 flex items-center justify-center">
                    <i class="fas fa-exclamation-triangle text-2xl text-red-500"></i>
                </div>
                <p class="text-gray-400">Failed to load history. Make sure the backend is running.</p>
            </div>
        `);
    } finally {
        hideLoading();
    }
}

function displayHistory(historyItems) {
    $('#historyResults').empty();
    
    if (!historyItems || historyItems.length === 0) {
        $('#historyResults').html(`
            <div class="text-center py-16 border-2 border-dashed border-gray-800 rounded-2xl">
                <div class="w-16 h-16 mx-auto mb-4 rounded-full border-2 border-gold/30 bg-gold/10 flex items-center justify-center">
                    <i class="fas fa-history text-2xl text-gold"></i>
                </div>
                <p class="text-gray-400">No saved items yet. Start by asking questions or generating content.</p>
            </div>
        `);
        return;
    }
    
    historyItems.forEach(item => {
        const type = (item.type || item.interaction_type || 'item').toLowerCase();
        const topic = item.topic || 'general';
        const timestamp = item.timestamp || item.created_at || '';
        const question = item.question || topic;
        const content = item.content || '';
        const document = item.document || item.filename || 'Unknown';
        
        let contentHtml = '';
        
        // Format based on type
        if (type === 'flashcards') {
            contentHtml = formatHistoryFlashcards(content);
        } else if (type === 'mcqs') {
            contentHtml = formatHistoryMCQs(content);
        } else if (type === 'chat') {
            contentHtml = formatHistoryChat(content);
        } else {
            contentHtml = `<p class="text-gray-400 text-sm leading-relaxed whitespace-pre-wrap">${escapeHtml(content.substring(0, 500))}${content.length > 500 ? '...' : ''}</p>`;
        }
        
        const historyHtml = `
            <div class="bg-dark-light border border-gray-800 rounded-2xl p-6 fade-in card-hover">
                <div class="flex flex-wrap gap-2 mb-3">
                    <span class="inline-flex items-center px-3 py-1 rounded-full bg-gold/10 border border-gold/30 text-gold text-xs font-semibold uppercase">
                        <i class="fas fa-${type === 'chat' ? 'comments' : type === 'mcqs' ? 'question-circle' : 'layer-group'} mr-1.5"></i>
                        ${escapeHtml(type)}
                    </span>
                    <span class="inline-flex items-center px-3 py-1 rounded-full bg-gray-800/50 border border-gray-700 text-gray-400 text-xs font-medium">
                        <i class="fas fa-tag mr-1.5"></i>${escapeHtml(topic)}
                    </span>
                    <span class="inline-flex items-center px-3 py-1 rounded-full bg-gray-800/50 border border-gray-700 text-gray-400 text-xs font-medium">
                        <i class="fas fa-file-pdf mr-1.5"></i>${escapeHtml(document.substring(0, 20))}${document.length > 20 ? '...' : ''}
                    </span>
                    ${timestamp ? `<span class="inline-flex items-center px-3 py-1 rounded-full bg-gray-800/50 border border-gray-700 text-gray-500 text-xs">
                        <i class="fas fa-clock mr-1.5"></i>${escapeHtml(timestamp)}
                    </span>` : ''}
                </div>
                <h4 class="font-display text-lg font-semibold text-white mb-4">${escapeHtml(question)}</h4>
                <div class="max-h-96 overflow-y-auto pr-2">
                    ${contentHtml}
                </div>
            </div>
        `;
        
        $('#historyResults').append(historyHtml);
    });
}

function formatHistoryChat(content) {
    return `
        <div class="bg-gray-800/30 border border-gray-700 rounded-xl p-4">
            <div class="text-xs font-semibold uppercase tracking-wider text-green-400 mb-2">
                <i class="fas fa-robot mr-1"></i>Answer
            </div>
            <p class="text-gray-300 text-sm leading-relaxed">${escapeHtml(content)}</p>
        </div>
    `;
}

function formatHistoryFlashcards(content) {
    const cards = parseFlashcards(content);
    
    if (cards.length === 0) {
        return `<p class="text-gray-400 text-sm">${escapeHtml(content.substring(0, 300))}</p>`;
    }
    
    let html = '<div class="space-y-3">';
    cards.forEach((card, index) => {
        html += `
            <div class="bg-gray-800/30 border border-gray-700 rounded-xl overflow-hidden">
                <div class="bg-gradient-to-r from-gold/10 to-gold/5 border-b border-gold/20 p-3">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-xs font-bold uppercase tracking-wider text-gold">
                            <i class="fas fa-layer-group mr-1"></i>Card #${String(index + 1).padStart(2, '0')}
                        </span>
                    </div>
                    <div class="text-xs font-semibold text-gold/70 mb-1">FRONT:</div>
                    <p class="text-sm text-white font-medium">${escapeHtml(card.front)}</p>
                </div>
                <div class="p-3">
                    <div class="text-xs font-semibold text-green-400/70 mb-1">BACK:</div>
                    <p class="text-sm text-gray-300">${escapeHtml(card.back)}</p>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    return html;
}

function formatHistoryMCQs(content) {
    const mcqs = parseMCQs(content);
    
    if (mcqs.length === 0) {
        return `<p class="text-gray-400 text-sm">${escapeHtml(content.substring(0, 300))}</p>`;
    }
    
    let html = '<div class="space-y-4">';
    mcqs.forEach((mcq, index) => {
        html += `
            <div class="bg-gray-800/30 border border-gray-700 rounded-xl p-4">
                <div class="text-xs font-bold uppercase tracking-wider text-gold mb-2">
                    <i class="fas fa-question-circle mr-1"></i>Question ${String(index + 1).padStart(2, '0')}
                </div>
                <p class="text-sm font-semibold text-white mb-3">${escapeHtml(mcq.question)}</p>
                <div class="space-y-2">
                    ${Object.entries(mcq.options).map(([letter, text]) => {
                        const isCorrect = letter === mcq.correct;
                        return `
                            <div class="flex items-center gap-2 p-2 rounded-lg ${isCorrect ? 'bg-green-500/10 border border-green-500/30' : 'bg-gray-800/50'}">
                                <span class="flex-shrink-0 w-6 h-6 rounded ${isCorrect ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-400'} flex items-center justify-center text-xs font-bold">
                                    ${letter}
                                </span>
                                <span class="text-xs ${isCorrect ? 'text-green-300 font-medium' : 'text-gray-400'}">${escapeHtml(text)}</span>
                                ${isCorrect ? '<i class="fas fa-check-circle text-green-400 ml-auto"></i>' : ''}
                            </div>
                        `;
                    }).join('')}
                </div>
                ${mcq.correct ? `
                    <div class="mt-3 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/30 text-green-400 text-xs font-semibold">
                        <i class="fas fa-check-circle"></i>
                        Correct Answer: ${mcq.correct}
                    </div>
                ` : ''}
            </div>
        `;
    });
    html += '</div>';
    
    return html;
}

// Parsing Functions
function parseMCQs(raw) {
    const mcqs = [];
    const blocks = raw.split(/(?=(?:Q\d*[:\.]|^\d+[\.)])\s)/m);
    
    blocks.forEach(block => {
        block = block.trim();
        if (!block) return;
        
        const qMatch = block.match(/(?:Q\d*[:.]\s*|^\d+[.)]\s*)(.+?)(?=\n[A-D][.):]|\nA[.):])/s);
        if (!qMatch) return;
        
        const question = qMatch[1].trim();
        const options = {};
        
        ['A', 'B', 'C', 'D'].forEach(letter => {
            const m = block.match(new RegExp(`${letter}[.):\\s]+(.+?)(?=\\n[A-D][.):\\s]|Correct|Answer|$)`, 'is'));
            if (m) options[letter] = m[1].trim();
        });
        
        const correctMatch = block.match(/(?:Correct|Answer)[:\s]+([A-D])/i);
        const correct = correctMatch ? correctMatch[1].toUpperCase() : '';
        
        if (question && Object.keys(options).length > 0) {
            mcqs.push({ question, options, correct });
        }
    });
    
    return mcqs;
}

function parseFlashcards(raw) {
    const cards = [];
    const lines = raw.trim().split('\n');
    let front = null;
    let back = [];
    
    const frontMarker = /^(?:FRONT|QUESTION|front|question)\s*[:\-.)]\s*|^Q\s*[:\-.)]\s*/i;
    const backMarker = /^(?:BACK|ANSWER|back|answer)\s*[:\-.)]\s*|^A\s*[:\-.)]\s*/i;
    
    lines.forEach(line => {
        line = line.trim();
        if (!line) return;
        
        if (frontMarker.test(line)) {
            if (front && back.length > 0) {
                cards.push({ front, back: back.join('\n').trim() });
            }
            front = line.replace(frontMarker, '').trim();
            back = [];
        } else if (backMarker.test(line)) {
            const content = line.replace(backMarker, '').trim();
            if (content) back.push(content);
        } else if (front !== null) {
            back.push(line);
        }
    });
    
    if (front && back.length > 0) {
        cards.push({ front, back: back.join('\n').trim() });
    }
    
    return cards;
}

// UI Helpers
function updateDocumentStatus(filename, processed) {
    if (processed) {
        $('#statusPill').html(`
            <span class="w-2 h-2 rounded-full bg-green-500 pulse-gold"></span>
            ${filename.substring(0, 30)}${filename.length > 30 ? '...' : ''}
        `).removeClass('bg-gray-800/50 border-gray-700 text-gray-400')
          .addClass('bg-green-500/10 border-green-500/30 text-green-400');
        
        $('#docStatus').text('✓');
        $('#docStatusText').text('Indexed & ready');
    }
}

function updateStats() {
    $('#questionsCount').text(questionsAsked || '—');
}

function showLoading(text) {
    $('#loadingText').text(text);
    $('#loadingOverlay').removeClass('hidden').addClass('fade-in');
}

function hideLoading() {
    $('#loadingOverlay').addClass('hidden');
}

function showNotification(message, type) {
    const bgColor = type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-gold';
    const notification = $(`
        <div class="fixed top-4 right-4 ${bgColor} text-white px-6 py-3 rounded-xl shadow-lg z-50 fade-in">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} mr-2"></i>
            ${message}
        </div>
    `);
    
    $('body').append(notification);
    setTimeout(() => notification.fadeOut(() => notification.remove()), 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
