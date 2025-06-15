// Simple model persistence for Chainlit MCP Client
(function() {
    if (window.chainlitModelManager) return;
    window.chainlitModelManager = true;
    
    const STORAGE_KEY = 'chainlit_selected_model';
    
    // Save just the model name
    function saveModel(modelName) {
        try {
            localStorage.setItem(STORAGE_KEY, modelName);
            console.log('🟢 MODEL SAVED:', modelName);
            return true;
        } catch (error) {
            console.error('🔴 FAILED TO SAVE MODEL:', error);
            return false;
        }
    }
    
    // Load just the model name
    function loadModel() {
        try {
            const model = localStorage.getItem(STORAGE_KEY);
            console.log('🔍 LOADED MODEL:', model || 'NO MODEL FOUND');
            return model;
        } catch (error) {
            console.error('🔴 FAILED TO LOAD MODEL:', error);
            return null;
        }
    }
    
    // Listen for messages from Chainlit
    window.addEventListener('message', (event) => {
        if (event.data && typeof event.data === 'string') {
            try {
                const message = JSON.parse(event.data);
                
                if (message.type === 'SAVE_MODEL') {
                    console.log('💾 SAVE MODEL REQUEST:', message.model);
                    const success = saveModel(message.model);
                    window.postMessage(JSON.stringify({
                        type: 'MODEL_SAVED',
                        success: success,
                        model: message.model
                    }), '*');
                }
                
                else if (message.type === 'LOAD_MODEL') {
                    console.log('📖 LOAD MODEL REQUEST');
                    const model = loadModel();
                    window.postMessage(JSON.stringify({
                        type: 'MODEL_LOADED',
                        model: model
                    }), '*');
                }
            } catch (error) {
                console.error('🔴 ERROR PROCESSING MESSAGE:', error);
            }
        }
    });
    
    console.log('🎯 SIMPLE MODEL MANAGER INITIALIZED');
})();
