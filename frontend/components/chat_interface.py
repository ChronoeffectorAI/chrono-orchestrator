from chainlit import Component

class ChatInterface(Component):
    def render(self):
        return """
        <div>
            <h1>Welcome to the AI Chat Interface</h1>
            <input type="text" id="userInput" placeholder="Type your query here...">
            <button onclick="sendQuery()">Send</button>
            <div id="response"></div>
        </div>
        <script>
            function sendQuery() {
                const userInput = document.getElementById('userInput').value;
                fetch('/api/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ input: userInput })
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('response').innerText = data.response;
                });
            }
        </script>
        """ 