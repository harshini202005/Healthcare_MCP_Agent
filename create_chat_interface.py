#!/usr/bin/env python3

html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Healthcare Assistant - AI Chat</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            height: 95vh;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2em;
            margin-bottom: 5px;
        }

        .header p {
            opacity: 0.9;
            font-size: 0.95em;
        }

        .main-content {
            padding: 20px 30px;
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .messages-area {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
            margin-bottom: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .message {
            max-width: 75%;
            padding: 12px 18px;
            border-radius: 18px;
            word-wrap: break-word;
            animation: slideIn 0.3s ease;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message.user {
            align-self: flex-end;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 4px;
        }

        .message.assistant {
            align-self: flex-start;
            background: white;
            border: 1px solid #e9ecef;
            border-bottom-left-radius: 4px;
        }

        .message.system {
            align-self: center;
            background: #fff3cd;
            border: 1px solid #ffc107;
            color: #856404;
            font-size: 0.9em;
            max-width: 85%;
            text-align: center;
        }

        .message-content {
            white-space: pre-wrap;
            line-height: 1.5;
        }

        .message-time {
            font-size: 0.75em;
            opacity: 0.7;
            margin-top: 5px;
        }

        .input-area {
            display: flex;
            gap: 12px;
            align-items: flex-end;
        }

        .input-wrapper {
            flex: 1;
            position: relative;
        }

        #userInput {
            width: 100%;
            padding: 14px 18px;
            border: 2px solid #dee2e6;
            border-radius: 25px;
            font-size: 1em;
            font-family: inherit;
            resize: none;
            max-height: 120px;
            overflow-y: auto;
            transition: border-color 0.3s;
        }

        #userInput:focus {
            outline: none;
            border-color: #667eea;
        }

        .send-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px 28px;
            font-size: 1.1em;
            font-weight: 600;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            white-space: nowrap;
        }

        .send-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }

        .send-btn:disabled {
            background: #6c757d;
            cursor: not-allowed;
            transform: none;
        }

        .examples {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }

        .example-chip {
            background: white;
            border: 1px solid #dee2e6;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            cursor: pointer;
            transition: all 0.2s;
        }

        .example-chip:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }

        .typing-indicator {
            display: flex;
            gap: 4px;
            padding: 10px 15px;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            background: #667eea;
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }

        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes typing {
            0%, 60%, 100% {
                transform: translateY(0);
            }
            30% {
                transform: translateY(-10px);
            }
        }

        .welcome-message {
            text-align: center;
            padding: 40px 20px;
            color: #6c757d;
        }

        .welcome-message h2 {
            margin-bottom: 15px;
            color: #495057;
        }

        .welcome-icon {
            font-size: 3em;
            margin-bottom: 15px;
        }

        .hidden {
            display: none !important;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.5em;
            }
            
            .message {
                max-width: 85%;
            }

            .examples {
                flex-direction: column;
            }

            .example-chip {
                text-align: center;
            }

            .container {
                height: 100vh;
                border-radius: 0;
            }

            body {
                padding: 0;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 Healthcare Assistant</h1>
            <p>AI-Powered Health Management System</p>
        </div>

        <div class="main-content">
            <div class="chat-container">
                <div class="messages-area" id="messagesArea">
                    <div class="welcome-message" id="welcomeMessage">
                        <div class="welcome-icon">🏥</div>
                        <h2>Hello! I'm your Healthcare Assistant</h2>
                        <p>Ask me anything about health, nutrition, or book an appointment!</p>
                        
                        <div class="examples" style="margin-top: 25px; justify-content: center;">
                            <div class="example-chip" onclick="fillExample(\\'What are the benefits of drinking water?\\')">
                                💧 Benefits of water
                            </div>
                            <div class="example-chip" onclick="fillExample(\\'Generate a vegetarian diet plan for 2000 calories\\')">
                                🥗 Vegetarian diet plan
                            </div>
                            <div class="example-chip" onclick="fillExample(\\'Book an appointment for PAT001 tomorrow at 10 AM for general checkup\\')">
                                📅 Book appointment
                            </div>
                        </div>
                    </div>
                </div>

                <div class="input-area">
                    <div class="input-wrapper">
                        <textarea 
                            id="userInput" 
                            placeholder="Type your message... (e.g., \\'Give me a keto diet plan\\' or \\'Book appointment for PAT123\\')"
                            rows="1"
                            onkeydown="handleKeyPress(event)"
                        ></textarea>
                    </div>
                    <button class="send-btn" onclick="sendMessage()" id="sendBtn">Send 🚀</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = 'http://localhost:8000';
        let isProcessing = false;

        function fillExample(text) {
            document.getElementById('userInput').value = text;
            document.getElementById('userInput').focus();
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            
            if (!message || isProcessing) return;
            
            document.getElementById('welcomeMessage').classList.add('hidden');
            addMessage(message, 'user');
            input.value = '';
            input.style.height = 'auto';
            
            const { tool, args } = analyzeQuery(message);
            
            let toolName = {
                'general_query': '💬 General Health Query',
                'generate_diet': '🥗 Diet Plan Generator',
                'book_appointment': '📅 Appointment Booking'
            }[tool] || 'Processing';
            
            addMessage(`Using: ${toolName}`, 'system');
            
            const typingId = showTypingIndicator();
            isProcessing = true;
            document.getElementById('sendBtn').disabled = true;
            
            try {
                const response = await fetch(`${API_BASE}/mcp/call`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: tool, args })
                });
                
                const result = await response.json();
                removeTypingIndicator(typingId);
                const formattedResponse = formatResponse(result, tool);
                addMessage(formattedResponse, 'assistant');
                
            } catch (error) {
                removeTypingIndicator(typingId);
                addMessage(`❌ Error: ${error.message}`, 'assistant');
            } finally {
                isProcessing = false;
                document.getElementById('sendBtn').disabled = false;
            }
        }

        function analyzeQuery(query) {
            const lowerQuery = query.toLowerCase();
            
            if (lowerQuery.match(/book|appointment|schedule|reserve|doctor visit|consultation/)) {
                return detectBookingDetails(query);
            }
            
            if (lowerQuery.match(/diet|meal plan|nutrition|food|eat|vegetarian|vegan|keto|calories|weight loss|menu/)) {
                return detectDietDetails(query);
            }
            
            return { tool: 'general_query', args: { question: query } };
        }

        function detectBookingDetails(query) {
            const args = {};
            
            const patientMatch = query.match(/PAT\\w+/i);
            if (patientMatch) {
                args.user_id = patientMatch[0].toUpperCase();
            } else {
                const idMatch = query.match(/(?:patient|id|for)\\s+(\\w+)/i);
                if (idMatch) args.user_id = idMatch[1];
            }
            
            let timeStr = '';
            const timePatterns = [
                /(\\d{1,2}:\\d{2}\\s*(?:AM|PM))/i,
                /(\\d{1,2}\\s*(?:AM|PM))/i,
                /(tomorrow|today|next week|monday|tuesday|wednesday|thursday|friday|saturday|sunday)/i
            ];
            
            for (const pattern of timePatterns) {
                const match = query.match(pattern);
                if (match) timeStr += ' ' + match[1];
            }
            
            if (timeStr) args.time = parseTimeString(timeStr.trim());
            
            const specialties = ['cardiology', 'dermatology', 'orthopedics', 'pediatrics', 'neurology', 'general'];
            for (const specialty of specialties) {
                if (query.toLowerCase().includes(specialty)) {
                    args.specialty = specialty === 'general' ? 'general-practice' : specialty;
                    break;
                }
            }
            
            const reasonMatch = query.match(/(?:for|regarding)\\s+(.+?)(?:\\s+at|\\s+on|\\s+tomorrow|$)/i);
            if (reasonMatch) args.reason = reasonMatch[1].trim();
            
            return { tool: 'book_appointment', args };
        }

        function detectDietDetails(query) {
            const args = {};
            
            const preferences = {
                'vegetarian': 'vegetarian', 'vegan': 'vegan', 'keto': 'keto',
                'low-carb': 'low-carb', 'low carb': 'low-carb',
                'high-protein': 'high-protein', 'high protein': 'high-protein',
                'diabetic': 'diabetic-friendly',
                'gluten-free': 'gluten-free', 'gluten free': 'gluten-free',
                'balanced': 'balanced'
            };
            
            for (const [key, value] of Object.entries(preferences)) {
                if (query.toLowerCase().includes(key)) {
                    args.preferences = value;
                    break;
                }
            }
            
            if (!args.preferences) args.preferences = 'balanced';
            
            const calorieMatch = query.match(/(\\d{3,4})\\s*(?:cal|calorie)/i);
            if (calorieMatch) args.calories = parseInt(calorieMatch[1]);
            
            const allergyMatch = query.match(/(?:allergy|allergies|allergic to|avoid)\\s+(?:to\\s+)?([a-z\\s,]+?)(?:\\s+and|\\s+$|\\.)/i);
            if (allergyMatch) {
                args.allergies = allergyMatch[1].split(/,|\\s+and\\s+/).map(a => a.trim()).filter(a => a);
            }
            
            return { tool: 'generate_diet', args };
        }

        function parseTimeString(timeStr) {
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            
            const hourMatch = timeStr.match(/(\\d{1,2})\\s*(?::(\\d{2}))?\\s*(AM|PM)/i);
            if (hourMatch) {
                let hour = parseInt(hourMatch[1]);
                const minute = hourMatch[2] ? parseInt(hourMatch[2]) : 0;
                const meridiem = hourMatch[3].toUpperCase();
                
                if (meridiem === 'PM' && hour !== 12) hour += 12;
                if (meridiem === 'AM' && hour === 12) hour = 0;
                
                tomorrow.setHours(hour, minute, 0, 0);
            } else {
                tomorrow.setHours(10, 0, 0, 0);
            }
            
            return tomorrow.toISOString().slice(0, 16);
        }

        function addMessage(content, type) {
            const messagesArea = document.getElementById('messagesArea');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;
            messageDiv.appendChild(contentDiv);
            
            if (type !== 'system') {
                const timeDiv = document.createElement('div');
                timeDiv.className = 'message-time';
                timeDiv.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                messageDiv.appendChild(timeDiv);
            }
            
            messagesArea.appendChild(messageDiv);
            messagesArea.scrollTop = messagesArea.scrollHeight;
        }

        function showTypingIndicator() {
            const messagesArea = document.getElementById('messagesArea');
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message assistant';
            typingDiv.id = 'typing-' + Date.now();
            typingDiv.innerHTML = `
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            `;
            
            messagesArea.appendChild(typingDiv);
            messagesArea.scrollTop = messagesArea.scrollHeight;
            return typingDiv.id;
        }

        function removeTypingIndicator(id) {
            const element = document.getElementById(id);
            if (element) element.remove();
        }

        function formatResponse(data, tool) {
            let output = '';
            
            if (data.error) {
                output += `❌ ${data.message || 'An error occurred'}\\n\\n`;
                if (data.fallback) output += `💡 ${data.fallback}\\n`;
                if (data.suggestion) output += `\\n💡 Suggestion: ${data.suggestion}\\n`;
                return output.trim();
            }
            
            if (tool === 'book_appointment' && data.confirmation_number) {
                output += `✅ ${data.message}\\n\\n`;
                output += `🎫 Confirmation: ${data.confirmation_number}\\n\\n`;
                
                if (data.details) {
                    output += `📋 Details:\\n`;
                    for (const [key, value] of Object.entries(data.details)) {
                        output += `   • ${key}: ${value}\\n`;
                    }
                }
                
                if (data.instructions) {
                    output += `\\n📌 Instructions:\\n`;
                    data.instructions.forEach(inst => output += `   ${inst}\\n`);
                }
            }
            else if (tool === 'generate_diet' && data.plan) {
                output += `✅ ${data.message}\\n\\n`;
                
                if (typeof data.plan === 'string') {
                    output += data.plan;
                } else {
                    output += '📅 Your Meal Plan:\\n\\n';
                    for (const [meal, food] of Object.entries(data.plan)) {
                        output += `${meal}:\\n${food}\\n\\n`;
                    }
                }
                
                if (data.preference) output += `\\n🥗 Preference: ${data.preference}\\n`;
                if (data.daily_calories) output += `📊 Calories: ${data.daily_calories}\\n`;
                
                if (data.tips) {
                    output += '\\n💡 Tips:\\n';
                    data.tips.forEach(tip => output += `   ${tip}\\n`);
                }
            }
            else if (tool === 'general_query' && data.answer) {
                output += data.answer;
                if (data.disclaimer) output += `\\n\\n${data.disclaimer}`;
            }
            else {
                output = JSON.stringify(data, null, 2);
            }
            
            return output.trim();
        }

        document.getElementById('userInput').addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    </script>
</body>
</html>'''

# Write the HTML file
with open('/Users/pradeep.j/Desktop/Healthcare/frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ Chat interface created successfully!")
print("📁 File: /Users/pradeep.j/Desktop/Healthcare/frontend/index.html")
print("🚀 Open it in your browser to start chatting!")
