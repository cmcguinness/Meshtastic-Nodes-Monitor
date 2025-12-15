/**
 * Node Configuration JavaScript
 * Handles form submissions, validation, and reboot management
 */

// Track if changes require reboot
let rebootRequired = false;
// Store pending config changes
let pendingConfigSection = null;
let pendingConfigData = null;
let pendingChannelIndex = null;

/**
 * Initialize all configuration forms
 * This is called after the modal content is loaded
 */
function initializeConfigForms() {
    // Get all forms in the config modal
    const forms = document.querySelectorAll('#configModal form[data-section]');

    console.log(`Found ${forms.length} config forms to initialize`);

    forms.forEach(form => {
        // Remove any existing listeners to avoid duplicates
        const newForm = form.cloneNode(true);
        form.parentNode.replaceChild(newForm, form);

        newForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Form submitted:', this.dataset.section);
            handleConfigSave(this);
        });
    });
}

/**
 * Handle configuration form submission
 */
function handleConfigSave(form) {
    const section = form.dataset.section;
    const channelIndex = form.dataset.channelIndex; // For channel forms
    const formData = new FormData(form);
    const data = {};

    // Convert FormData to object, handling different input types
    for (const [key, value] of formData.entries()) {
        const input = form.querySelector(`[name="${key}"]`);

        if (input.type === 'checkbox') {
            data[key] = input.checked;
        } else if (input.type === 'number') {
            data[key] = parseInt(value);
        } else if (input.tagName === 'SELECT') {
            // Convert select values to integers if they're numeric
            const numValue = parseInt(value);
            data[key] = isNaN(numValue) ? value : numValue;
        } else if (value !== '' && value !== '********') {
            // Skip empty password fields
            data[key] = value;
        }
    }

    // Handle unchecked checkboxes (they don't appear in FormData)
    form.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        if (!formData.has(checkbox.name)) {
            data[checkbox.name] = false;
        }
    });

    // Special handling for position config - convert decimal lat/lon to integer format
    if (section === 'position') {
        // Convert fixed_latitude and fixed_longitude from decimal to integer format
        if (data.fixed_latitude !== undefined && data.fixed_latitude !== '') {
            data.latitude_i = Math.round(parseFloat(data.fixed_latitude) * 10000000);
            delete data.fixed_latitude; // Remove the decimal field
        }
        if (data.fixed_longitude !== undefined && data.fixed_longitude !== '') {
            data.longitude_i = Math.round(parseFloat(data.fixed_longitude) * 10000000);
            delete data.fixed_longitude; // Remove the decimal field
        }
        if (data.fixed_altitude !== undefined && data.fixed_altitude !== '') {
            data.altitude = parseInt(data.fixed_altitude);
            delete data.fixed_altitude; // Remove the renamed field
        }
    }

    console.log('Form data prepared for save:', data);

    // Show confirmation dialog
    showConfigConfirmation(section, data, channelIndex);
}

/**
 * Show confirmation dialog before saving
 */
function showConfigConfirmation(section, data, channelIndex = null) {
    // Store the pending changes globally
    pendingConfigSection = section;
    pendingConfigData = data;
    pendingChannelIndex = channelIndex;

    console.log('Showing confirmation for section:', section, 'with data:', data);

    const sectionNames = {
        'device': 'Device',
        'lora': 'LoRa',
        'channel': 'Channel',
        'position': 'Position',
        'power': 'Power',
        'network': 'Network',
        'display': 'Display',
        'bluetooth': 'Bluetooth',
        'security': 'Security',
        'mqtt': 'MQTT',
        'serial': 'Serial',
        'telemetry': 'Telemetry',
        'store_forward': 'Store & Forward',
        'external_notification': 'External Notification',
        'range_test': 'Range Test',
        'neighbor_info': 'Neighbor Info',
        'detection_sensor': 'Detection Sensor',
        'audio': 'Audio',
        'remote_hardware': 'Remote Hardware',
        'ambient_lighting': 'Ambient Lighting',
        'paxcounter': 'Paxcounter',
        'canned_message': 'Canned Message'
    };

    const sectionName = section === 'channel' && channelIndex !== null
        ? `Channel ${channelIndex}`
        : (sectionNames[section] || section);

    // Special warnings for certain sections
    let warningMessage = '';
    if (section === 'network') {
        warningMessage = '<div class="alert alert-warning">Changing network settings may disconnect you from the device.</div>';
    } else if (section === 'lora') {
        warningMessage = '<div class="alert alert-warning">Changing LoRa settings may disconnect the device or violate local regulations.</div>';
    }

    const confirmHTML = `
        <div class="modal fade" id="configConfirmModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Confirm Configuration Change</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${warningMessage}
                        <p>Are you sure you want to save changes to <strong>${sectionName}</strong> configuration?</p>
                        <p class="text-muted small">The device will be rebooted automatically after saving.</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="confirmSaveBtn">Save & Reboot</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove any existing confirm modal
    const existingModal = document.getElementById('configConfirmModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add new modal
    document.body.insertAdjacentHTML('beforeend', confirmHTML);

    // Show the modal
    const confirmModal = new bootstrap.Modal(document.getElementById('configConfirmModal'));
    confirmModal.show();

    // Add event listener to the confirm button
    document.getElementById('confirmSaveBtn').addEventListener('click', function() {
        confirmConfigSave();
    });
}

/**
 * Confirm and save configuration
 */
function confirmConfigSave() {
    // Use the globally stored pending changes
    const section = pendingConfigSection;
    const data = pendingConfigData;
    const channelIndex = pendingChannelIndex;

    console.log('Confirming save for section:', section, 'with data:', data, 'channelIndex:', channelIndex);

    // Close confirmation modal
    const confirmModal = bootstrap.Modal.getInstance(document.getElementById('configConfirmModal'));
    if (confirmModal) {
        confirmModal.hide();
    }

    // Show loading toast
    showConfigToast('Saving configuration...', 'info');

    // Determine the correct endpoint
    const endpoint = section === 'channel' && channelIndex !== null
        ? `/api/config/channel/${channelIndex}`
        : `/api/config/${section}`;

    // Send POST request to save config
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        console.log('Response status:', response.status);
        return response.json();
    })
    .then(result => {
        console.log('Save result:', result);
        if (result.success) {
            showConfigToast('Configuration saved successfully', 'success');

            // Check if reboot is required
            if (result.reboot_required) {
                rebootRequired = true;
                setTimeout(() => {
                    rebootDevice();
                }, 1500);
            }
        } else {
            showConfigToast(`Error saving configuration: ${result.error}`, 'danger');
        }
    })
    .catch(error => {
        console.error('Save error:', error);
        showConfigToast(`Error saving configuration: ${error.message}`, 'danger');
    });
}

/**
 * Reboot the device
 */
function rebootDevice() {
    showConfigToast('Rebooting device...', 'info');

    fetch('/api/config/reboot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            // Show reboot status modal with countdown
            showRebootStatusModal();
        } else {
            showConfigToast(`Error rebooting device: ${result.error}`, 'danger');
        }
    })
    .catch(error => {
        showConfigToast(`Error rebooting device: ${error.message}`, 'danger');
    });
}

/**
 * Show reboot status modal with countdown timer
 */
function showRebootStatusModal() {
    // Close the config modal
    if (window.configModal) {
        window.configModal.hide();
    }

    const rebootHTML = `
        <div class="modal fade" id="rebootStatusModal" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-warning text-dark">
                        <h5 class="modal-title">
                            <i class="bi bi-arrow-clockwise me-2"></i>Device Rebooting
                        </h5>
                    </div>
                    <div class="modal-body text-center">
                        <div class="mb-3">
                            <div class="spinner-border text-warning" role="status" style="width: 3rem; height: 3rem;">
                                <span class="visually-hidden">Rebooting...</span>
                            </div>
                        </div>
                        <p class="mb-2" id="rebootStatus">Device is rebooting...</p>
                        <p class="text-muted small mb-0" id="rebootTimer">Waiting for device to come back online...</p>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove any existing reboot modal
    const existingModal = document.getElementById('rebootStatusModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add new modal
    document.body.insertAdjacentHTML('beforeend', rebootHTML);

    // Show the modal
    const rebootModal = new bootstrap.Modal(document.getElementById('rebootStatusModal'));
    rebootModal.show();

    // Start countdown and reconnection polling
    startReconnectionPolling();
}

/**
 * Poll for device reconnection with countdown timer
 */
function startReconnectionPolling() {
    let elapsedSeconds = 0;
    const rebootDelay = 15; // Wait 15 seconds for device to actually reboot
    const maxAttempts = 75; // Try for 75 seconds total (15s reboot + 60s polling)
    let pollInterval = null;

    // Update timer every second
    const timerInterval = setInterval(() => {
        elapsedSeconds++;
        const timerElement = document.getElementById('rebootTimer');
        const statusElement = document.getElementById('rebootStatus');

        if (timerElement) {
            if (elapsedSeconds < rebootDelay) {
                // During reboot phase
                const remaining = rebootDelay - elapsedSeconds;
                timerElement.textContent = `Rebooting... (${remaining}s)`;
            } else {
                // During polling phase
                const pollingTime = elapsedSeconds - rebootDelay;
                timerElement.textContent = `Waiting for reconnection... (${pollingTime}s)`;
            }
        }

        // Start polling after reboot delay
        if (elapsedSeconds === rebootDelay && statusElement) {
            statusElement.textContent = 'Checking connection...';

            // Start polling for reconnection every 2 seconds
            pollInterval = setInterval(() => {
                checkDeviceConnectivity()
                    .then(isConnected => {
                        if (isConnected) {
                            clearInterval(timerInterval);
                            clearInterval(pollInterval);
                            showReconnectionSuccess(elapsedSeconds);
                        }
                    })
                    .catch(error => {
                        console.log('Still waiting for device...', error);
                    });
            }, 2000);

            window.rebootPollInterval = pollInterval;
        }

        if (elapsedSeconds >= maxAttempts) {
            clearInterval(timerInterval);
            if (pollInterval) {
                clearInterval(pollInterval);
            }
            showReconnectionFailure();
        }
    }, 1000);

    // Store intervals globally so we can clear them if needed
    window.rebootTimerInterval = timerInterval;
}

/**
 * Check if device is back online
 */
async function checkDeviceConnectivity() {
    try {
        const response = await fetch('/api/config/device', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            signal: AbortSignal.timeout(5000) // 5 second timeout
        });

        if (response.ok) {
            const data = await response.json();
            return data.success !== false; // Consider it connected if we get valid data
        }
        return false;
    } catch (error) {
        return false; // Connection still not available
    }
}

/**
 * Show reconnection success and auto-refresh config
 */
function showReconnectionSuccess(elapsedSeconds) {
    const statusElement = document.getElementById('rebootStatus');
    const timerElement = document.getElementById('rebootTimer');

    if (statusElement && timerElement) {
        statusElement.innerHTML = '<i class="bi bi-check-circle-fill text-success me-2"></i>Device reconnected!';
        timerElement.textContent = `Reconnected after ${elapsedSeconds}s`;
    }

    showConfigToast('Device reconnected successfully!', 'success');

    // Wait 2 seconds then close modal and reload config
    setTimeout(() => {
        const rebootModal = bootstrap.Modal.getInstance(document.getElementById('rebootStatusModal'));
        if (rebootModal) {
            rebootModal.hide();
        }

        // Remove modal from DOM
        const modalElement = document.getElementById('rebootStatusModal');
        if (modalElement) {
            modalElement.remove();
        }

        // Reload the config page to show updated values
        showConfigToast('Refreshing configuration...', 'info');
        setTimeout(() => {
            showConfigInfo(); // Reopen the config modal with fresh data
        }, 500);
    }, 2000);
}

/**
 * Show reconnection failure message
 */
function showReconnectionFailure() {
    const statusElement = document.getElementById('rebootStatus');
    const timerElement = document.getElementById('rebootTimer');

    if (statusElement && timerElement) {
        statusElement.innerHTML = '<i class="bi bi-exclamation-triangle-fill text-danger me-2"></i>Device not responding';
        timerElement.textContent = 'Please check your connection and try again.';
    }

    showConfigToast('Device did not reconnect. Please check connection.', 'danger');

    // Add a close button to the modal
    const modalElement = document.getElementById('rebootStatusModal');
    if (modalElement) {
        const modalHeader = modalElement.querySelector('.modal-header');
        if (modalHeader && !modalHeader.querySelector('.btn-close')) {
            modalHeader.innerHTML = `
                <h5 class="modal-title">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>Connection Timeout
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            `;
            modalHeader.classList.remove('bg-warning', 'text-dark');
            modalHeader.classList.add('bg-danger', 'text-white');
        }
    }
}

/**
 * Show toast notification using the main app's showToast function
 */
function showConfigToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        console.log(message);
        return;
    }

    const bgClass = {
        'info': 'bg-info',
        'success': 'bg-success',
        'warning': 'bg-warning',
        'danger': 'bg-danger'
    }[type] || 'bg-info';

    const toastHTML = `
        <div class="toast align-items-center text-white ${bgClass} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHTML);

    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 3000
    });

    toast.show();

    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}
