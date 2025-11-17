/**
 * ============================================
 * UNIFIED MODAL SYSTEM - Game TopUp
 * Professional notification system
 * ============================================
 */

class Modal {
    constructor() {
        this.createModalContainer();
    }

    createModalContainer() {
        // Check if modal container already exists
        if (document.getElementById('unified-modal-container')) {
            return;
        }

        const modalHTML = `
            <!-- Unified Modal Container -->
            <div id="unified-modal-container" class="fixed inset-0 z-50 hidden overflow-y-auto">
                <!-- Backdrop -->
                <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity" id="modal-backdrop"></div>

                <!-- Modal Dialog -->
                <div class="flex min-h-screen items-center justify-center p-4">
                    <div class="relative bg-white rounded-lg shadow-xl max-w-md w-full transform transition-all" id="modal-dialog">
                        <!-- Modal Header -->
                        <div class="modal-header px-6 py-4 border-b" id="modal-header">
                            <div class="flex items-center justify-between">
                                <div class="flex items-center">
                                    <div class="modal-icon mr-3 text-2xl" id="modal-icon"></div>
                                    <h3 class="text-lg font-bold text-gray-900" id="modal-title"></h3>
                                </div>
                                <button type="button" class="text-gray-400 hover:text-gray-600 transition" id="modal-close-btn">
                                    <i class="fas fa-times text-xl"></i>
                                </button>
                            </div>
                        </div>

                        <!-- Modal Body -->
                        <div class="modal-body px-6 py-4" id="modal-body">
                            <p class="text-gray-700" id="modal-message"></p>
                            <div id="modal-extra-content"></div>
                        </div>

                        <!-- Modal Footer -->
                        <div class="modal-footer px-6 py-4 border-t bg-gray-50 rounded-b-lg" id="modal-footer">
                            <div class="flex justify-end space-x-3" id="modal-actions"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Close on backdrop click
        document.getElementById('modal-backdrop')?.addEventListener('click', () => {
            this.hide();
        });

        // Close on X button
        document.getElementById('modal-close-btn')?.addEventListener('click', () => {
            this.hide();
        });

        // Close on ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hide();
            }
        });
    }

    show(options) {
        const {
            type = 'info',
            title = '',
            message = '',
            html = null,
            actions = null,
            autoClose = false,
            autoCloseDelay = 3000,
            onClose = null
        } = options;

        // Set icon and header color based on type
        const iconConfig = this.getIconConfig(type);
        const modalIcon = document.getElementById('modal-icon');
        const modalHeader = document.getElementById('modal-header');
        const modalTitle = document.getElementById('modal-title');
        const modalMessage = document.getElementById('modal-message');
        const modalExtraContent = document.getElementById('modal-extra-content');
        const modalActions = document.getElementById('modal-actions');

        // Set icon
        modalIcon.innerHTML = iconConfig.icon;
        modalIcon.className = `modal-icon mr-3 text-2xl ${iconConfig.color}`;

        // Set header
        modalHeader.className = `modal-header px-6 py-4 border-b ${iconConfig.headerBg}`;
        modalTitle.textContent = title;
        modalTitle.className = `text-lg font-bold ${iconConfig.textColor}`;

        // Set message
        if (html) {
            modalMessage.innerHTML = '';
            modalExtraContent.innerHTML = html;
        } else {
            modalMessage.textContent = message;
            modalExtraContent.innerHTML = '';
        }

        // Set actions
        modalActions.innerHTML = '';
        if (actions && actions.length > 0) {
            actions.forEach(action => {
                const button = this.createButton(action);
                modalActions.appendChild(button);
            });
        } else {
            // Default "Close" button
            const button = this.createButton({
                label: 'Đóng',
                style: 'secondary',
                onClick: () => this.hide()
            });
            modalActions.appendChild(button);
        }

        // Show modal
        const container = document.getElementById('unified-modal-container');
        container.classList.remove('hidden');
        document.body.style.overflow = 'hidden';

        // Auto close
        if (autoClose) {
            setTimeout(() => {
                this.hide();
                if (onClose) onClose();
            }, autoCloseDelay);
        }

        // Store onClose callback
        this.onCloseCallback = onClose;
    }

    hide() {
        const container = document.getElementById('unified-modal-container');
        container.classList.add('hidden');
        document.body.style.overflow = '';

        if (this.onCloseCallback) {
            this.onCloseCallback();
            this.onCloseCallback = null;
        }
    }

    getIconConfig(type) {
        const configs = {
            success: {
                icon: '<i class="fas fa-check-circle"></i>',
                color: 'text-green-500',
                headerBg: 'bg-green-50',
                textColor: 'text-green-900'
            },
            error: {
                icon: '<i class="fas fa-exclamation-circle"></i>',
                color: 'text-red-500',
                headerBg: 'bg-red-50',
                textColor: 'text-red-900'
            },
            warning: {
                icon: '<i class="fas fa-exclamation-triangle"></i>',
                color: 'text-yellow-500',
                headerBg: 'bg-yellow-50',
                textColor: 'text-yellow-900'
            },
            info: {
                icon: '<i class="fas fa-info-circle"></i>',
                color: 'text-blue-500',
                headerBg: 'bg-blue-50',
                textColor: 'text-blue-900'
            },
            question: {
                icon: '<i class="fas fa-question-circle"></i>',
                color: 'text-purple-500',
                headerBg: 'bg-purple-50',
                textColor: 'text-purple-900'
            }
        };

        return configs[type] || configs.info;
    }

    createButton(action) {
        const button = document.createElement('button');
        button.type = 'button';
        button.textContent = action.label || 'OK';

        // Button styles
        const styles = {
            primary: 'px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 transition transform hover:scale-105',
            secondary: 'px-4 py-2 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 transition',
            success: 'px-4 py-2 bg-green-500 text-white font-semibold rounded-lg hover:bg-green-600 transition',
            danger: 'px-4 py-2 bg-red-500 text-white font-semibold rounded-lg hover:bg-red-600 transition',
            warning: 'px-4 py-2 bg-yellow-500 text-white font-semibold rounded-lg hover:bg-yellow-600 transition'
        };

        button.className = styles[action.style || 'primary'];

        if (action.icon) {
            button.innerHTML = `<i class="${action.icon} mr-2"></i>${action.label || 'OK'}`;
        }

        button.addEventListener('click', () => {
            if (action.onClick) {
                action.onClick();
            }
            if (action.closeAfter !== false) {
                this.hide();
            }
        });

        return button;
    }

    // Convenience methods
    success(title, message, options = {}) {
        this.show({
            type: 'success',
            title,
            message,
            ...options
        });
    }

    error(title, message, options = {}) {
        this.show({
            type: 'error',
            title,
            message,
            ...options
        });
    }

    warning(title, message, options = {}) {
        this.show({
            type: 'warning',
            title,
            message,
            ...options
        });
    }

    info(title, message, options = {}) {
        this.show({
            type: 'info',
            title,
            message,
            ...options
        });
    }

    confirm(title, message, onConfirm, onCancel = null) {
        this.show({
            type: 'question',
            title,
            message,
            actions: [
                {
                    label: 'Hủy',
                    style: 'secondary',
                    onClick: () => {
                        if (onCancel) onCancel();
                    }
                },
                {
                    label: 'Xác nhận',
                    style: 'primary',
                    icon: 'fas fa-check',
                    onClick: () => {
                        if (onConfirm) onConfirm();
                    }
                }
            ]
        });
    }

    prompt(title, message, onSubmit, defaultValue = '') {
        const html = `
            <div class="mt-4">
                <input
                    type="text"
                    id="prompt-input"
                    value="${defaultValue}"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="${message}"
                >
            </div>
        `;

        this.show({
            type: 'question',
            title,
            message: '',
            html,
            actions: [
                {
                    label: 'Hủy',
                    style: 'secondary'
                },
                {
                    label: 'OK',
                    style: 'primary',
                    onClick: () => {
                        const value = document.getElementById('prompt-input').value;
                        if (onSubmit) onSubmit(value);
                    }
                }
            ]
        });

        // Focus input after modal shows
        setTimeout(() => {
            document.getElementById('prompt-input')?.focus();
        }, 100);
    }
}

// Initialize modal when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (!window.modal) {
        window.modal = new Modal();
        window.showModal = window.modal;
        console.log('✅ Modal system initialized');
    }
});

// Also create immediately for immediate access
if (!window.modal) {
    window.modal = new Modal();
    window.showModal = window.modal;
}

// Optional: Override native alert/confirm (use with caution)
if (typeof window.OVERRIDE_NATIVE_DIALOGS !== 'undefined' && window.OVERRIDE_NATIVE_DIALOGS) {
    window.originalAlert = window.alert;
    window.originalConfirm = window.confirm;
    window.originalPrompt = window.prompt;

    window.alert = function(message) {
        window.modal.info('Thông báo', message);
    };

    window.confirm = function(message) {
        return new Promise((resolve) => {
            window.modal.confirm('Xác nhận', message,
                () => resolve(true),
                () => resolve(false)
            );
        });
    };

    window.prompt = function(message, defaultValue = '') {
        return new Promise((resolve) => {
            window.modal.prompt('Nhập liệu', message,
                (value) => resolve(value),
                defaultValue
            );
        });
    };
}
