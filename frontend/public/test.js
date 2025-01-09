console.log("test.js loaded");

// Check if Phantom is installed
const isPhantomInstalled = window.phantom?.solana?.isPhantom;
console.log("Phantom installed:", isPhantomInstalled);

// Create and append overlay
function createOverlay() {
    console.log("Creating overlay");
    const overlay = document.createElement('div');
    overlay.id = 'wallet-overlay';
    document.body.appendChild(overlay);
    return overlay;
}

// Create authentication popup
function createWalletAuthPopup() {
    console.log("Creating wallet popup");
    
    // Check if popup already exists
    const existingOverlay = document.getElementById('wallet-overlay');
    const existingPopup = document.getElementById('wallet-popup');
    
    if (existingOverlay || existingPopup) {
        console.log("Popup already exists, removing old one");
        existingOverlay?.remove();
        existingPopup?.remove();
    }
    
    createOverlay();
    
    // Create popup container
    const popup = document.createElement('div');
    popup.id = 'wallet-popup';

    // Add content based on Phantom installation status
    if (isPhantomInstalled) {
        console.log("Showing Phantom connect option");
        popup.innerHTML = `
            <div class="wallet-popup-content">
                <div class="wallet-header">
                    <img src="./public/logo_light.png" alt="Logo" class="app-logo">
                    <h2>Welcome to ChronoeffectorAI</h2>
                    <p class="subtitle">Connect your wallet to continue</p>
                </div>
                
                <div class="wallet-options">
                    <button id="connectPhantom" class="wallet-button phantom">
                        <img src="https://developers.moralis.com/wp-content/uploads/2023/11/Phantom-Wallet.png" alt="Phantom">
                        <span>Connect with Phantom</span>
                        <div class="hover-effect"></div>
                    </button>
                    
                    <div class="coming-soon">
                        <button class="wallet-button disabled">
                            <img src="https://raw.githubusercontent.com/solflare-wallet/solflare-snap/refs/heads/master/logo.svg" alt="Solflare">
                            <span>Solflare (Coming Soon)</span>
                        </button>
                    </div>
                </div>

                <div class="wallet-footer">
                    <p>By connecting, you agree to our <a href="#">Terms of Service</a></p>
                </div>
            </div>
        `;
    } else {
        console.log("Showing Phantom install option");
        popup.innerHTML = `
            <div class="wallet-popup-content">
                <div class="wallet-header">
                    <img src="https://chronoeffector.ai/logo.png" alt="Logo" class="app-logo">
                    <h2>Wallet Required</h2>
                    <p class="subtitle">Please install Phantom Wallet to continue</p>
                </div>
                
                <div class="install-section">
                    <img src="https://www.phantom.app/img/logo.png" alt="Phantom" class="phantom-large">
                    <a href="https://phantom.app/" target="_blank" class="install-button">
                        Install Phantom
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="external-link">
                            <path d="M21 13v10h-21v-19h12v2h-10v15h17v-8h2zm3-12h-10.988l4.035 4-6.977 7.07 2.828 2.828 6.977-7.07 4.125 4.172v-11z"/>
                        </svg>
                    </a>
                    <p class="install-note">Refresh this page after installing</p>
                </div>

                <div class="wallet-footer">
                    <p>Need help? <a href="#" class="help-link">Watch Tutorial</a></p>
                </div>
            </div>
        `;
    }

    // Add popup to page
    document.body.appendChild(popup);
    console.log("Popup added to body");
    
    // Debug: Check if elements are actually in the DOM
    console.log("Overlay in DOM:", !!document.getElementById('wallet-overlay'));
    console.log("Popup in DOM:", !!document.getElementById('wallet-popup'));

    // Add connect functionality if Phantom is installed
    if (isPhantomInstalled) {
        const connectButton = document.getElementById('connectPhantom');
        if (connectButton) {
            connectButton.addEventListener('click', connectWallet);
            console.log("Connect button listener added");
        } else {
            console.error("Connect button not found in DOM");
        }
        
        // Add hover animation listener
        connectButton?.addEventListener('mousemove', (e) => {
            const rect = e.target.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            connectButton.style.setProperty('--mouse-x', `${x}px`);
            connectButton.style.setProperty('--mouse-y', `${y}px`);
        });
    }
}

// Function to connect to Phantom wallet
async function connectWallet() {
    try {
        const resp = await window.phantom?.solana?.connect();
        const publicKey = resp.publicKey.toString();
        
        // Remove the auth popup and overlay with fade out
        const popup = document.getElementById('wallet-popup');
        const overlay = document.getElementById('wallet-overlay');
        popup.classList.add('fade-out');
        overlay.classList.add('fade-out');
        
        setTimeout(() => {
            popup.remove();
            overlay.remove();
        }, 500);
        
        // Show success message
        showSuccessMessage(publicKey);
        
        // Enable the Chainlit app
        document.body.classList.add('authenticated');
        
    } catch (err) {
        showErrorMessage();
    }
}

function showSuccessMessage(publicKey) {
    const toast = document.createElement('div');
    toast.className = 'toast success';
    toast.innerHTML = `
        <div class="toast-content">
            <div class="toast-icon">✓</div>
            <div class="toast-message">
                <h4>Successfully Connected</h4>
                <p>${publicKey.slice(0, 4)}...${publicKey.slice(-4)}</p>
            </div>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function showErrorMessage() {
    const toast = document.createElement('div');
    toast.className = 'toast error';
    toast.innerHTML = `
        <div class="toast-content">
            <div class="toast-icon">×</div>
            <div class="toast-message">
                <h4>Connection Failed</h4>
                <p>Please try again</p>
            </div>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Check if user is already connected
async function checkConnection() {
    console.log("Checking connection...");
    
    // If Phantom is not installed, show install popup immediately
    if (!isPhantomInstalled) {
        console.log("Phantom not installed, showing install popup");
        createWalletAuthPopup();
        return false;
    }

    try {
        const address = await getCurrentWalletAddress();
        if (address) {
            console.log("Already Connected:", address);
            document.body.classList.add('authenticated');
            return true;
        }
    } catch (err) {
        console.log("Not connected, showing connect popup");
        createWalletAuthPopup();
        return false;
    }
}

// Add this function to get the current wallet address
async function getCurrentWalletAddress() {
    console.log("Getting current wallet address...");
    try {
        const provider = window.phantom?.solana;
        if (provider) {
            console.log("Provider found");
            // Check if already connected
            const resp = await provider.connect({ onlyIfTrusted: true });
            console.log("Provider response:", resp);
            return resp?.publicKey?.toString() || null;
        }
        console.log("No provider found");
        return null;
    } catch (err) {
        console.log("Error getting wallet address:", err);
        return null;
    }
}

// Function to fetch token holdings
async function getTokenHoldings(walletAddress) {
    try {
        // Using public Solana RPC endpoint (you might want to use your own endpoint)
        const response = await fetch(`https://api.mainnet-beta.solana.com`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [
                    walletAddress,
                    {
                        "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
                    },
                    {
                        "encoding": "jsonParsed"
                    }
                ]
            })
        });
        const data = await response.json();
        return data.result?.value || [];
    } catch (err) {
        console.error('Error fetching token holdings:', err);
        return [];
    }
}

// Function to show holdings popup
function showHoldingsPopup(holdings) {
    const overlay = document.createElement('div');
    overlay.className = 'holdings-overlay';
    
    const popup = document.createElement('div');
    popup.className = 'holdings-popup';
    
    popup.innerHTML = `
        <div class="holdings-header">
            <h3>Wallet Holdings</h3>
            <button class="close-button">×</button>
        </div>
        <div class="holdings-content">
            ${holdings.length > 0 ? `
                <div class="holdings-list">
                    ${holdings.map(holding => `
                        <div class="token-item">
                            <div class="token-info">
                                <span class="token-amount">${holding.account.data.parsed.info.tokenAmount.uiAmount}</span>
                                <span class="token-symbol">${holding.account.data.parsed.info.mint.slice(0, 4)}...${holding.account.data.parsed.info.mint.slice(-4)}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            ` : '<p class="no-tokens">No tokens found</p>'}
        </div>
    `;

    overlay.appendChild(popup);
    document.body.appendChild(overlay);

    // Close button handler
    const closeButton = popup.querySelector('.close-button');
    closeButton.onclick = () => {
        overlay.classList.add('fade-out');
        setTimeout(() => overlay.remove(), 300);
    };

    // Click outside to close
    overlay.onclick = (e) => {
        if (e.target === overlay) {
            overlay.classList.add('fade-out');
            setTimeout(() => overlay.remove(), 300);
        }
    };
}

// Updated addTestButton function
function addTestButton() {
    const walletDisplay = document.createElement('div');
    walletDisplay.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: var(--primary-color);
        padding: 12px 16px;
        border-radius: 12px;
        box-shadow: 0 4px 12px var(--purple-glow);
        cursor: pointer;
        z-index: 9998;
        display: flex;
        align-items: center;
        gap: 8px;
        transition: all 0.3s ease;
    `;

    const walletIcon = document.createElement('div');
    walletIcon.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 7h-1V6a3 3 0 0 0-3-3H5a3 3 0 0 0-3 3v12a3 3 0 0 0 3 3h14a3 3 0 0 0 3-3v-8a3 3 0 0 0-3-3zm-1 9h-2a2 2 0 0 1 0-4h2v4zm2-4h-4a1 1 0 0 0 0 2h4v3a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1H9a1 1 0 0 0 0 2h10a1 1 0 0 1 1 1v3z" fill="white"/>
        </svg>
    `;

    const addressText = document.createElement('span');
    addressText.style.cssText = `
        color: white;
        font-weight: 600;
        font-size: 14px;
    `;

    // Update address display
    async function updateDisplay() {
        console.log("Updating wallet display...");
        const address = await getCurrentWalletAddress();
        console.log("Current address:", address);

        if (address) {
            const displayAddress = `${address.slice(0, 4)}...${address.slice(-4)}`;
            console.log("Display address:", displayAddress);
            addressText.textContent = displayAddress;
            walletDisplay.style.display = 'flex';
            
            // Add click handler to show holdings
            walletDisplay.onclick = async () => {
                console.log("Fetching holdings for address:", address);
                const holdings = await getTokenHoldings(address);
                console.log("Holdings:", holdings);
                showHoldingsPopup(holdings);
            };
        } else {
            console.log("No wallet connected");
            addressText.textContent = "Connect Wallet";
            walletDisplay.style.display = 'flex'; // Always show
            walletDisplay.onclick = () => {
                console.log("Opening connect popup");
                createWalletAuthPopup();
            };
        }
    }

    // Assemble the display
    walletDisplay.appendChild(walletIcon);
    walletDisplay.appendChild(addressText);
    document.body.appendChild(walletDisplay);
    console.log("Wallet display added to DOM");

    // Initial update
    updateDisplay();

    // Update periodically
    setInterval(updateDisplay, 2000);

    // Debug: Check if element is in DOM
    console.log("Wallet display in DOM:", !!document.querySelector('[style*="position: fixed"]'));
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded");
    setTimeout(() => {
        console.log("Starting initialization");
        checkConnection().then(() => {
            console.log("Connection check complete");
            addTestButton();
        });
    }, 100);
});
