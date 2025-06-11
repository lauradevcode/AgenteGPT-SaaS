document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.perfil').forEach(perfil => {
        perfil.addEventListener('click', async () => {
            const tipo = perfil.dataset.perfil;
            const statusDiv = document.getElementById('status');
            
            try {
                statusDiv.style.display = 'block';
                statusDiv.style.background = '#f0f9ff';
                statusDiv.textContent = 'Ativando perfil...';
                
                const response = await fetch('/ativar-perfil', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ perfil: tipo })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    statusDiv.style.background = '#ecfdf5';
                    statusDiv.textContent = `✅ ${data.message}`;
                    
                    // Teste de envio de mensagem
                    const whatsappResponse = await fetch('/testar');
                    const whatsappData = await whatsappResponse.json();
                    console.log('Resposta WhatsApp:', whatsappData);
                } else {
                    throw new Error(data.error || 'Erro desconhecido');
                }
            } catch (error) {
                statusDiv.style.background = '#fee2e2';
                statusDiv.textContent = `❌ Erro: ${error.message}`;
                console.error('Erro:', error);
            }
        });
    });
});