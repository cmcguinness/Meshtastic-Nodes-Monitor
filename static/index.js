let pause_update = false;   // Keep refreshes from happlening when a dropdown is open

// function do_pause(yesno) {
//     pause_update = Boolean(yesno);
// }

function showToast(message) {
    const toastContainer = document.querySelector('.toast-container');

    const toastHTML = `
            <div class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <strong class="me-auto">Notification</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
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

// [Previous JavaScript code remains the same]
// Settings management
let updateInterval;
let maxRows = 50;


// Update the refresh interval
function updateRefreshInterval(rate) {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
    updateInterval = setInterval(updateTables, rate * 1000);

}

document.addEventListener('DOMContentLoaded', function () {
    const dropdownItems = document.querySelectorAll('.dropdown-item');
    dropdownItems.forEach(item => {
        item.addEventListener('click', function (event) {
            event.preventDefault();
            const selectedValue = this.getAttribute('data-value');
            handleSelectionChange(selectedValue);
        });
    });
});

function handleSelectionChange(value) {
    updateRefreshInterval(parseInt(value));
    showToast(`Changed refresh rate to ${value} seconds.`)
}

function updateTables() {
    if (pause_update) {
        return;
    }

    console.log('updateTables()...');
    fetch(`/api/updates?rowmax=${settings.maxRows}`)
        .then(response => response.json())
        .then(data => {
            console.log('Data: ', data);
            if (data.hasOwnProperty('flash') && data['flash'] !== null) {
                window.alert(data.flash)
            }
            // Update summary table
            const summaryHeaders = document.getElementById('summary-headers');
            const summaryValues = document.getElementById('summary-values');

            // Clear existing content
            summaryHeaders.innerHTML = '';
            summaryValues.innerHTML = '';

            // Add new content
            data.summary.columns.forEach(column => {
                summaryHeaders.innerHTML += `<th>${column}</th>`;
            });
            data.summary.values.forEach(value => {
                summaryValues.innerHTML += `<td>${value}</td>`;
            });

            // Update messages table
            const messagesBody = document.querySelector('#messages-table tbody');
            messagesBody.innerHTML = '';
            data.messages.forEach(msg => {
                messagesBody.innerHTML += `
                            <tr>
                                <td>${msg.datetime}</td>
                                <td>${msg.from}</td>
                                <td>${msg.to}</td>
                                <td>${msg.channel}</td>
                                <td>${msg.message}</td>
                            </tr>
                        `;
            });

            // Update packets table
            const packetsBody = document.querySelector('#packets-table tbody');
            packetsBody.innerHTML = '';
            data.packets.forEach(packet => {
                packetsBody.innerHTML += `
                            <tr>
                                <td>${packet.datetime}</td>
                                <td>${packet.node}</td>
                                <td>${packet.hops}</td>
                                <td>${packet.rssi}</td>
                                <td>${packet.type}</td>
                                <td>${packet.information}</td>
                            </tr>
                        `;
            });
        })
        .catch(error => console.error('Error fetching updates:', error));
}

// Initial update
updateTables();

// Set up polling every 5 seconds
setInterval(updateTables, 5000);

function initializeTableActions(tableId) {
    document.getElementById(tableId).addEventListener('click', function (event) {
        const dropdownItem = event.target.closest('.dropdown-item');
        if (!dropdownItem) return;

        event.preventDefault();

        const row = dropdownItem.closest('tr');
        if (!row) {
            console.error('Could not find associated table row');
            return;
        }

        const cells = Array.from(row.cells);

        const rowData = {
            dateTime: cells[0]?.textContent.trim(),
            node: cells[1]?.textContent.trim(),
            hops: cells[2]?.textContent.trim(),
            rssi: cells[3]?.textContent.trim(),
            type: cells[4]?.textContent.trim(),
            information: cells[5]?.textContent.trim(),
            action: dropdownItem.textContent.trim()
        };

        handleAction(rowData);
    });
}

function handleAction(rowData) {
    console.log('Action triggered for packet:', rowData);

    const matches = rowData.node.match(/!([^\n]*)/);

    let node_id = '';
    if (matches) {
        node_id = matches[1];
    }
    console.log(`Captured ${rowData.action}`);

    switch (rowData.action) {
        case 'View Details':
            showDetailsModal(node_id);
            break;
        case 'Trace Route':
            traceRoute(node_id);
            break;
        case 'Open in Map':
            openMap(node_id);
            break;
        default:
            console.log('Unknown action:', rowData.action);
    }
}

function traceRoute(rowData) {
    console.log(`Trace Route ${rowData}`);

    fetch(`/api/traceroute?id=${encodeURIComponent(rowData)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        }).then(msg => {
        showToast(msg);
    })
        .catch(error => {
            showToast(`Error: ${error.message}`);
        });
}

function openMap(rowData) {
    const nodeNum = parseInt(rowData, 16)
    window.open('https://meshtastic.liamcottle.net/?node_id=' + String(nodeNum), "_blank");
}

// Initialize the modal
let modal = null;

function showDetailsModal(id) {
    if (!modal) {
        modal = new bootstrap.Modal(document.getElementById('dynamicModal'));
    }

    const modalBody = document.querySelector('#dynamicModal .modal-body');
    modalBody.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';

    modal.show();

    fetch(`/api/details?id=${encodeURIComponent(id)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(html => {
            modalBody.innerHTML = html;
        })
        .catch(error => {
            modalBody.innerHTML = `<div class="alert alert-danger">Error loading content: ${error.message}</div>`;
        });
}

initializeTableActions("packets-table");