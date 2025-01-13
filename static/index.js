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
let updateInterval = setInterval(updateTables, 5000);
let updateIntervalSeconds = 5;
let maxRows = 50;

// Update the refresh interval
function updateRefreshInterval(rate) {
    if (updateInterval) {
        clearInterval(updateInterval);

    }
    updateInterval = setInterval(updateTables, rate * 1000);
    updateIntervalSeconds = rate;

}


function restoreSettings() {
    document.getElementById("maxrows").value = maxRows.toString();
    document.getElementById("refreshtime").value = updateIntervalSeconds.toString();
    showToast('Settings Restored');
}

function updateSettings() {
    maxRows = parseInt(document.getElementById("maxrows").value);
    updateIntervalSeconds = parseInt(document.getElementById("refreshtime").value);
    updateRefreshInterval(updateIntervalSeconds);
    showToast("Settings Updated");
}


function changeMaxRows() {
    maxRows = parseInt(document.getElementById("maxrows").value);
    // console.log(`new maxrows ${maxrows}`)
}

document.addEventListener('DOMContentLoaded', function () {
    const dropdownItems = document.querySelectorAll('#refreshtime .dropdown-item');
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
    if (document.querySelector('ul.show') !== null) {
        console.log('Dropdown open, snoozing refresh')
        return;
    }

    console.log('updateTables()...');
    fetch(`/api/updates?rowmax=${maxRows}`)
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
            const doEncrypted = document.getElementById('include-encrypted').checked
            messagesBody.innerHTML = '';
            data.messages.forEach(msg => {
                if (doEncrypted || msg.message !== '*** ENCRYPTED TEXT ***') {
                    messagesBody.innerHTML += `
                            <tr>
                                <td>${msg.datetime}</td>
                                <td>                                    
                                    <div class="dropdown">
                                        <a  class="dropdown-toggle text-decoration-none" href="#" role="button" data-bs-toggle="dropdown">
                                            ${msg.id}
                                        </a>
                                        <ul class="dropdown-menu">
                                            <li><a class="dropdown-item" href="#">View Details</a></li>
                                            <li><a class="dropdown-item" href="#">Open in Map</a></li>
                                            <li><a class="dropdown-item" href="#">Trace Route</a></li>    
                                        </ul>
                                    </div>
                                </td>
                                <td>${msg.from}</td>
                                <td>${msg.to}</td>
                                <td>${msg.channel}</td>
                                <td>${msg.message}</td>
                            </tr>
                        `;
                }
            });

            // Update nodes table
            const nodesBody = document.querySelector('#nodes-table tbody');
            nodesBody.innerHTML = '';
            data.nodes.forEach(node => {
                nodesBody.innerHTML += `
                            <tr>
                                <td>${node.lastHeard}</td>
                                <td>
                                    <div class="dropdown">
                                        <a  class="dropdown-toggle text-decoration-none" href="#" role="button" data-bs-toggle="dropdown">
                                            ${node.id}
                                        </a>
                                        <ul class="dropdown-menu">
                                            <li><a class="dropdown-item" href="#">View Details</a></li>
                                            <li><a class="dropdown-item" href="#">Open in Map</a></li>
                                            <li><a class="dropdown-item" href="#">Trace Route</a></li>    
                                        </ul>
                                    </div>
                                </td>
                                <td>${node.name}</td>
                                <td>${node.hwModel}</td>
                                <td>${node.hopsAway}</td>
                                <td>${node.distance}</td>
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
                                <td>
                                    <div class="dropdown">
                                        <a  class="dropdown-toggle text-decoration-none" href="#" role="button" data-bs-toggle="dropdown">
                                            ${packet.id}
                                        </a>
                                        <ul class="dropdown-menu">
                                            <li><a class="dropdown-item" href="#">View Details</a></li>
                                            <li><a class="dropdown-item" href="#">Open in Map</a></li>
                                            <li><a class="dropdown-item" href="#">Trace Route</a></li>    
                                        </ul>
                                    </div>
                                </td>
                                <td>${packet.name}</td>
                                <td>${packet.hops}</td>
                                <td>${packet.rssi}</td>
                                <td>${packet.type}</td>
                                <td>${packet.information}</td>
                            </tr>
                        `;
                reFilterPackets();
            });
        })
        .catch(error => console.error('Error fetching updates:', error));
}

// Initial update
updateTables();

// Set up polling every 5 seconds


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
            node: cells[1]?.textContent.trim(),
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

let lastPacketFilter = '';

function reFilterPackets() {
    const filterInput = document.getElementById('packet-filter');
    const filterText = lastPacketFilter;
    const rows = document.querySelectorAll('#packets-table tbody tr');

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(filterText) ? '' : 'none';
    });

}

// Initialize filter functionality
function initializePacketFilter() {
    const filterInput = document.getElementById('packet-filter');
    const applyFilterButton = document.getElementById('apply-filter');
    const resetFilterButton = document.getElementById('reset-filter');

    function filterPackets() {
        const filterText = filterInput.value.toLowerCase();
        lastPacketFilter = filterText;
        reFilterPackets();
        // document.getElementById("current-packet-filter").innerHTML = `Filtering List on "${filterText}"`;
        filterInput.placeholder = 'Filtering on "' + filterText + '"';
        filterInput.value = '';
    }

    function resetFilter() {
        filterInput.value = '';
        lastPacketFilter = '';
        reFilterPackets();
        // document.getElementById("current-packet-filter").innerHTML = '';
        filterInput.placeholder = 'Enter a Filter ...';
    }

    applyFilterButton.addEventListener('click', filterPackets);
    resetFilterButton.addEventListener('click', resetFilter);

    // Add Enter key support for the filter input
    filterInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            filterPackets();
        }
    });
}

initializeTableActions("packets-table");
initializeTableActions("nodes-table");
initializeTableActions("messages-table");

// Initialize the packet filter
initializePacketFilter();

// Create the tool tips

// Initialize Bootstrap tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
})