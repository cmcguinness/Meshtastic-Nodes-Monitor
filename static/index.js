// function do_pause(yesno) {
//     pause_update = Boolean(yesno);
// }

// Escape HTML to prevent XSS attacks
function escapeHtml(text) {
    if (text === null || text === undefined) {
        return '';
    }
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

function showToast(message) {
    const toastContainer = document.querySelector('.toast-container');

    const toastHTML = `
            <div class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <strong class="me-auto">Notification</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${escapeHtml(message)}
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
                showToast(data.flash)
            }
            // Update summary table
            const summaryHeaders = document.getElementById('summary-headers');
            const summaryValues = document.getElementById('summary-values');

            // Clear existing content
            summaryHeaders.innerHTML = '';
            summaryValues.innerHTML = '';

            const dropdown_menu = `
                                        <ul class="dropdown-menu">
                                            <li><a class="dropdown-item" href="#">View Details</a></li>
                                            <li><a class="dropdown-item" href="#">Open in Map</a></li>
                                            <li><a class="dropdown-item" href="#">Trace Route</a></li>    
                                            <li><a class="dropdown-item" href="#">DM Sender</a></li>    
                                        </ul>
                                        `

            // Add new content
            data.summary.columns.forEach(column => {
                summaryHeaders.innerHTML += `<th>${escapeHtml(column)}</th>`;
            });
            data.summary.values.forEach(value => {
                summaryValues.innerHTML += `<td>${escapeHtml(value)}</td>`;
            });

            // Update messages table
            const messagesBody = document.querySelector('#messages-table tbody');
            const doEncrypted = document.getElementById('include-encrypted').checked
            messagesBody.innerHTML = '';
            data.messages.forEach(msg => {
                if (doEncrypted || msg.message !== '*** ENCRYPTED TEXT ***') {
                    messagesBody.innerHTML += `
                            <tr>
                                <td>${escapeHtml(msg.datetime)}</td>
                                <td>
                                    <div class="dropdown">
                                        <a  class="dropdown-toggle text-decoration-none" href="#" role="button" data-bs-toggle="dropdown">
                                            ${escapeHtml(msg.id)}
                                        </a>
                                        ${dropdown_menu}
                                    </div>
                                </td>
                                <td>${escapeHtml(msg.from)}</td>
                                <td>${escapeHtml(msg.to)}</td>
                                <td>${escapeHtml(msg.channel)}</td>
                                <td>${escapeHtml(msg.message)}</td>
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
                                <td>${escapeHtml(node.lastHeard)}</td>
                                <td>
                                    <div class="dropdown">
                                        <a  class="dropdown-toggle text-decoration-none" href="#" role="button" data-bs-toggle="dropdown">
                                            ${escapeHtml(node.id)}
                                        </a>
                                         ${dropdown_menu}

                                    </div>
                                </td>
                                <td>${escapeHtml(node.name)}</td>
                                <td>${escapeHtml(node.hwModel)}</td>
                                <td>${escapeHtml(node.hopsAway)}</td>
                                <td>${escapeHtml(node.distance)}</td>
                            </tr>
                        `;
            });
            resortAfterDataRefresh()

            // Update packets table
            const packetsBody = document.querySelector('#packets-table tbody');
            packetsBody.innerHTML = '';
            data.packets.forEach(packet => {
                packetsBody.innerHTML += `
                            <tr>
                                <td>${escapeHtml(packet.datetime)}</td>
                                <td>
                                    <div class="dropdown">
                                        <a  class="dropdown-toggle text-decoration-none" href="#" role="button" data-bs-toggle="dropdown">
                                            ${escapeHtml(packet.id)}
                                        </a>
                                        ${dropdown_menu}
                                    </div>
                                </td>
                                <td>${escapeHtml(packet.name)}</td>
                                <td>${escapeHtml(packet.hops)}</td>
                                <td>${escapeHtml(packet.rssi)}</td>
                                <td>${escapeHtml(packet.type)}</td>
                                <td>${escapeHtml(packet.information)}</td>
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
        case 'DM Sender':
            showDmModal(node_id);
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
let details_modal = null;

function showDetailsModal(id) {
    if (!details_modal) {
        details_modal = new bootstrap.Modal(document.getElementById('detailsModal'));
    }

    const modalBody = document.querySelector('#detailsModal .modal-body');
    modalBody.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';

    details_modal.show();

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


// Initialize the modal
let dm_modal = null;

function showDmModal(id) {
    if (!dm_modal) {
        dm_modal = new bootstrap.Modal(document.getElementById('dmModal'));
    }

    const idfield = document.getElementById('dmId');
    idfield.innerText = id;

    const modalBody = document.querySelector('#dmModal .modal-body');

    dm_modal.show();

}

function sendDM() {
    const id = document.getElementById('dmId').innerText;
    const message = document.getElementById('dm-message').value;
    document.getElementById('dm-message').value = '';

    fetch(`/api/dm?id=${encodeURIComponent(id)}&message=${encodeURIComponent(message)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(msg => {
            showToast(msg);
            dm_modal.hide();
        })
        .catch(error => {
            showToast(`Error: ${error.message}`);
        });
}


// Initialize the modal
let channel_modal = null;

function showChannelModal(id, name) {
    if (!channel_modal) {
        channel_modal = new bootstrap.Modal(document.getElementById('channelModal'));
    }

    document.getElementById('channelName').innerText = name;;
    document.getElementById('channelId').innerText = id;

    channel_modal.show();

}

function sendChannel() {
    const id = document.getElementById('channelId').innerText;
    const message = document.getElementById('channelMessage').value;
    document.getElementById('channelMessage').value = '';
    fetch(`/api/sendchannel?id=${encodeURIComponent(id)}&message=${encodeURIComponent(message)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(msg => {
            showToast(msg);
            channel_modal.hide();
        })
        .catch(error => {
            showToast(`Error: ${error.message}`);
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


// Sorting the nodes list
// First, let's enhance the HTML with sort indicators
document.querySelectorAll('#nodes-table th').forEach(th => {
    th.style.cursor = 'pointer';
    // Add sort indicator span
    const indicator = document.createElement('span');
    indicator.className = 'sort-indicator ms-1';
    indicator.innerHTML = '↕️'; // Default state
    th.appendChild(indicator);
});

// Track current sort state
let currentSort = {
    column: null,
    ascending: true
};

// Function to update sort indicators
function updateSortIndicators(activeHeader) {
    document.querySelectorAll('#nodes-table th .sort-indicator').forEach(indicator => {
        if (indicator.parentElement === activeHeader) {
            indicator.innerHTML = currentSort.ascending ? '↑' : '↓';
        } else {
            indicator.innerHTML = '↕️';
        }
    });
}

// Function to compare values for sorting
function compareValues(a, b, ascending) {
    // Handle dates specifically for "Last Heard" column
    if (a instanceof Date && b instanceof Date) {
        return ascending ? a - b : b - a;
    }

    // Handle numeric values (like Hops Away and Distance)
    if (!isNaN(a) && !isNaN(b)) {
        return ascending ? a - b : b - a;
    }

    // Default string comparison
    const strA = String(a).toLowerCase();
    const strB = String(b).toLowerCase();
    return ascending ? strA.localeCompare(strB) : strB.localeCompare(strA);
}

// Main sorting function that can be called programmatically
function sortTable(columnIndex, ascending = null) {
    const tbody = document.querySelector('#nodes-table tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const th = document.querySelector(`#nodes-table th:nth-child(${columnIndex + 1})`);

    // If ascending is null, toggle the current direction
    if (ascending === null) {
        if (currentSort.column === columnIndex) {
            currentSort.ascending = !currentSort.ascending;
        } else {
            currentSort.ascending = true;
        }
    } else {
        currentSort.ascending = ascending;
    }

    currentSort.column = columnIndex;

    // Sort the rows
    rows.sort((rowA, rowB) => {
        let a = rowA.cells[columnIndex].textContent.trim();
        let b = rowB.cells[columnIndex].textContent.trim();

        // Convert to Date if it's the Last Heard column
        if (columnIndex === 0) {
            a = new Date(a);
            b = new Date(b);
        }
        // Convert to number for numeric columns
        else if (columnIndex === 4 || columnIndex === 5) {
            a = parseFloat(a);
            b = parseFloat(b);
        }

        return compareValues(a, b, currentSort.ascending);
    });

    // Update the DOM
    rows.forEach(row => tbody.appendChild(row));
    updateSortIndicators(th);
}

// Add click handlers to all headers
document.querySelectorAll('#nodes-table th').forEach((th, index) => {
    th.addEventListener('click', () => sortTable(index));
});

// Example of how to resort programmatically after data refresh
function resortAfterDataRefresh() {
    if (currentSort.column !== null) {
        sortTable(currentSort.column, currentSort.ascending);
    }
}