document.addEventListener('DOMContentLoaded', function() {

    // ===============================================
    // LÓGICA PARA A TELA DE LOGIN (login.html)
    // ===============================================
    const connectButtonLogin = document.querySelector('.btn-connect-agent');
    const whatsappInputLogin = document.querySelector('.login-input-whatsapp');

    if (connectButtonLogin && whatsappInputLogin) {
        // --- Lógica da Máscara para o input do WhatsApp ---
        whatsappInputLogin.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');

            if (value.length > 0) {
                value = value.substring(0, 11);

                if (value.length > 10) {
                    value = `(${value.substring(0, 2)}) ${value.substring(2, 7)}-${value.substring(7, 11)}`;
                } else if (value.length > 6) {
                    value = `(${value.substring(0, 2)}) ${value.substring(2, 6)}-${value.substring(6, 10)}`;
                } else if (value.length > 2) {
                    value = `(${value.substring(0, 2)}) ${value.substring(2, value.length)}`;
                } else if (value.length > 0) {
                    value = `(${value.substring(0, value.length)}`;
                }
            }
            e.target.value = value;
        });

        whatsappInputLogin.addEventListener('paste', function(e) {
            const pastedText = e.clipboardData.getData('text');
            e.target.value = pastedText.replace(/\D/g, '');
            e.preventDefault();
        });

        // --- Lógica do Botão "CONECTAR AGENTEGPT" na tela de login ---
        connectButtonLogin.addEventListener('click', function() {
            const rawNumber = whatsappInputLogin.value.replace(/\D/g, '');

            if (rawNumber.length !== 11) {
                alert('Por favor, digite um número de WhatsApp completo, incluindo o DDD (ex: (11) 99999-9999).');
                whatsappInputLogin.focus();
                return;
            }
            localStorage.setItem('whatsappNumber', rawNumber);
            window.location.href = 'cadastrarproduto.html';
        });
    }

    // ===============================================
    // LÓGICA PARA A TELA DE DASHBOARD (index.html)
    // ===============================================

    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', function(event) {
            event.preventDefault();
            localStorage.clear();
            window.location.href = 'login.html';
        });
    }

    // Acessando a div de mensagem de status pelo ID corrigido
    const statusMessage = document.getElementById('statusMessage');
    const profileCards = document.querySelectorAll('.profile-card');
    const activateProfileButton = document.getElementById('activateProfileButton');
    let selectedProfile = null;

    if (profileCards.length > 0 && statusMessage && activateProfileButton) {

        const loadActiveProfile = () => {
            const savedProfile = localStorage.getItem('selectedProfile');
            if (savedProfile) {
                profileCards.forEach(card => {
                    // Agora usa card.dataset.profile para corresponder ao HTML
                    if (card.dataset.profile === savedProfile) {
                        card.classList.add('active');
                        selectedProfile = savedProfile;
                        activateProfileButton.disabled = false; // Habilita o botão se já houver perfil salvo
                    } else {
                        card.classList.remove('active');
                    }
                });
            } else {
                activateProfileButton.disabled = true; // Desabilita se não houver perfil salvo
            }
        };

        loadActiveProfile();

        profileCards.forEach(card => {
            card.addEventListener('click', function() {
                // Remove a classe 'active' de todos os cards
                profileCards.forEach(pc => pc.classList.remove('active'));
                
                // Adiciona a classe 'active' ao card clicado
                this.classList.add('active');
                
                // Pega o valor de data-profile do card clicado
                selectedProfile = this.dataset.profile; 
                
                // Habilita o botão de ativar perfil
                activateProfileButton.disabled = false; 
                
                // Limpa e esconde a mensagem de status antiga
                statusMessage.style.display = 'none';
                statusMessage.textContent = '';
                
                // Salva o perfil selecionado no localStorage
                localStorage.setItem('selectedProfile', selectedProfile);
            });
        });

        activateProfileButton.addEventListener('click', async () => {
            if (!selectedProfile) {
                alert('Por favor, selecione um perfil antes de ativar.');
                return;
            }

            const storedProductData = localStorage.getItem('agenteGPTProductData');
            let productData = {};
            if (storedProductData) {
                try {
                    productData = JSON.parse(storedProductData);
                } catch (e) {
                    console.error("Erro ao fazer parse dos dados do produto do localStorage:", e);
                    alert("Erro ao carregar dados do produto. Por favor, recadastre o infoproduto.");
                    localStorage.removeItem('agenteGPTProductData'); // Limpa dados corrompidos
                    return;
                }
            } else {
                console.warn('Atenção: Nenhum infoproduto cadastrado. O agente funcionará de forma genérica até um produto ser cadastrado.');
            }

            try {
                statusMessage.style.display = 'block';
                statusMessage.style.background = '#f0f9ff'; // Cor para "processando"
                statusMessage.textContent = 'Ativando perfil... Por favor, aguarde.';
                activateProfileButton.disabled = true;

                const response = await fetch('/ativar-perfil', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        perfil: selectedProfile,
                        product_data: productData
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({error: 'Resposta não JSON ou vazia.'}));
                    throw new Error(errorData.error || `Erro HTTP: ${response.status} ${response.statusText}`);
                }

                const data = await response.json();

                if (data.success) {
                    statusMessage.style.background = '#ecfdf5'; // Cor para sucesso
                    statusMessage.textContent = `✅ Perfil '${selectedProfile.replace(/_/g, ' ')}' ativado com sucesso!`;
                    console.log('Prompt atual:', data.prompt_atual);
                    console.log('Status do Produto:', data.product_data_status);
                } else {
                    throw new Error(data.error || 'Erro desconhecido ao ativar perfil.');
                }
            } catch (error) {
                statusMessage.style.background = '#fee2e2'; // Cor para erro
                statusMessage.textContent = `❌ Erro: ${error.message}`;
                console.error('Erro ao ativar perfil:', error);
            } finally {
                activateProfileButton.disabled = false;
                setTimeout(() => {
                    statusMessage.style.display = 'none';
                }, 5000); // Esconde a mensagem após 5 segundos
            }
        });
    }

    // Botão Voltar da Dashboard (index.html)
    const backButtonIndex = document.getElementById('backButtonIndex');
    if (backButtonIndex) {
        backButtonIndex.addEventListener('click', function() {
            // Volta para a página de login, por exemplo
            window.location.href = 'login.html'; 
        });
    }


    // ===============================================
    // LÓGICA PARA A TELA DE CADASTRO DE PRODUTO (cadastrarproduto.html)
    // ===============================================

    const backButtonProduct = document.getElementById('backButton'); // Botão "Voltar" da tela de cadastro de produto
    const saveProductButton = document.getElementById('saveProductButton');
    const productNameInput = document.getElementById('productName');
    const saleLinkInput = document.getElementById('saleLink');
    const productDescriptionInput = document.getElementById('productDescription');
    const customKeywordsInput = document.getElementById('customKeywords');
    const descriptionCharCount = document.getElementById('descriptionCharCount');
    const suggestedKeywordCheckboxes = document.querySelectorAll('.suggested-keyword-checkbox');
    const descriptionMaxLength = 500;

    // Apenas aplica a lógica se os elementos essenciais da página de cadastro existirem
    if (productNameInput && saveProductButton) {

        // Ao carregar a página de cadastro de produto, preenche os campos com dados do localStorage
        const storedProductData = localStorage.getItem('agenteGPTProductData');
        let savedProduct = {};
        if (storedProductData) {
            try {
                savedProduct = JSON.parse(storedProductData);
            } catch (e) {
                console.error("Erro ao fazer parse dos dados do produto salvos:", e);
                localStorage.removeItem('agenteGPTProductData'); // Limpa dados corrompidos
            }
        }

        if (savedProduct.name) productNameInput.value = savedProduct.name;
        if (savedProduct.sale_link) saleLinkInput.value = savedProduct.sale_link;
        if (savedProduct.description) productDescriptionInput.value = savedProduct.description;

        // Lógica de preenchimento e marcação dos checkboxes de keywords
        if (savedProduct.keywords) {
            const savedKeywordsArray = savedProduct.keywords.split(',').map(kw => kw.trim().toLowerCase()).filter(kw => kw !== '');

            suggestedKeywordCheckboxes.forEach(checkbox => {
                if (savedKeywordsArray.includes(checkbox.value.toLowerCase())) {
                    checkbox.checked = true;
                } else {
                    checkbox.checked = false;
                }
            });

            const checkboxValues = Array.from(suggestedKeywordCheckboxes).map(cb => cb.value.toLowerCase());
            const customSavedKeywords = savedKeywordsArray.filter(kw => !checkboxValues.includes(kw));
            if (customKeywordsInput) {
                customKeywordsInput.value = customSavedKeywords.join(', ');
            }

        } else {
            suggestedKeywordCheckboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
            if (customKeywordsInput) {
                customKeywordsInput.value = '';
            }
        }

        // Lógica do contador de caracteres para Descrição do Produto
        if (productDescriptionInput && descriptionCharCount) {
            let currentLength = productDescriptionInput.value.length;
            if (currentLength > descriptionMaxLength) {
                productDescriptionInput.value = productDescriptionInput.value.substring(0, descriptionMaxLength);
                currentLength = descriptionMaxLength;
            }
            descriptionCharCount.textContent = `${currentLength}/${descriptionMaxLength} caracteres`;
            if (currentLength > descriptionMaxLength) {
                descriptionCharCount.style.color = 'red';
            } else {
                descriptionCharCount.style.color = '#555';
            }

            productDescriptionInput.addEventListener('input', function() {
                let currentLength = this.value.length;
                if (currentLength > descriptionMaxLength) {
                    this.value = this.value.substring(0, descriptionMaxLength);
                    currentLength = descriptionMaxLength;
                }
                descriptionCharCount.textContent = `${currentLength}/${descriptionMaxLength} caracteres`;
                if (currentLength > descriptionMaxLength) {
                    descriptionCharCount.style.color = 'red';
                } else {
                    descriptionCharCount.style.color = '#555';
                }
            });
        } else if (descriptionCharCount) {
            descriptionCharCount.textContent = `0/${descriptionMaxLength} caracteres`;
        }

        // Botão Voltar (redireciona para a página index.html)
        if (backButtonProduct) {
            backButtonProduct.addEventListener('click', function() {
                window.location.href = '../index.html'; // Volta para a dashboard
            });
        }

        // Lógica do botão "Salvar Infoproduto"
        saveProductButton.addEventListener('click', function() {
            const productName = productNameInput.value.trim();
            const saleLink = saleLinkInput.value.trim();
            const productDescription = productDescriptionInput.value.trim();

            // Validação simples do link de venda
            if (!saleLink.startsWith('http://') && !saleLink.startsWith('https://')) {
                alert('O link de venda deve começar com "http://" ou "https://".');
                saleLinkInput.focus();
                return;
            }

            let finalKeywordsArray = Array.from(suggestedKeywordCheckboxes)
                .filter(checkbox => checkbox.checked)
                .map(checkbox => checkbox.value.toLowerCase());

            const customKeywordsText = customKeywordsInput ? customKeywordsInput.value.trim() : '';
            if (customKeywordsText) {
                const customKeywordsParsed = customKeywordsText.split(',')
                    .map(kw => kw.trim().toLowerCase())
                    .filter(kw => kw.length > 0);
                finalKeywordsArray.push(...customKeywordsParsed);
            }

            const finalKeywords = Array.from(new Set(finalKeywordsArray)).sort().join(', ');

            if (!productName || !saleLink || !productDescription) {
                alert('Por favor, preencha todos os campos obrigatórios (Nome, Link de Venda, Descrição).');
                return;
            }

            const productDataToSave = {
                name: productName,
                sale_link: saleLink,
                keywords: finalKeywords,
                description: productDescription
            };

            localStorage.setItem('agenteGPTProductData', JSON.stringify(productDataToSave));

            console.log('--- Dados do Infoproduto Salvos ---');
            console.log('Dados Completos:', productDataToSave);
            console.log('-----------------------------------');
            console.log('Infoproduto salvo com sucesso! Redirecionando para a dashboard.');

            // Redireciona a página imediatamente após salvar no localStorage
            window.location.href = '../index.html';
        });
    }
});