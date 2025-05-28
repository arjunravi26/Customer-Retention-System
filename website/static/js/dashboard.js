// Initialize Tableau Dashboard
function initTableau() {
    const containerDiv = document.getElementById('viz1744952153280');
    const vizUrl = 'https://public.tableau.com/views/telcom_17449505978740/Dashboard1';
    const options = {
        hideTabs: true,
        hideToolbar: false,
        onFirstInteractive: () => {
            console.log('Tableau dashboard loaded');
        }
    };
    new tableau.Viz(containerDiv, vizUrl, options);
}

// Tab Switching
document.querySelectorAll('.tab-link').forEach(tab => {
    tab.addEventListener('click', () => {
        // Remove active from all tabs and hide all panes
        document.querySelectorAll('.tab-link').forEach(t => {
            t.classList.remove('active');
            t.setAttribute('aria-selected', 'false');
        });
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
            pane.classList.add('hidden');
        });

        // Add active to clicked tab and show corresponding pane
        tab.classList.add('active');
        tab.setAttribute('aria-selected', 'true');
        const targetPane = document.getElementById(tab.dataset.tab);
        targetPane.classList.remove('hidden');
        targetPane.classList.add('active');

        console.log(`Switched to tab: ${tab.dataset.tab}`);

        // Initialize Tableau only when dashboard tab is active
        if (tab.dataset.tab === 'dashboard') {
            initTableau();
        }
    });
});

// Customer Data Handling
let customers = [];
let originalCustomers = [];

async function fetchCustomers() {
    try {
        const response = await fetch('/api/customers');
        if (!response.ok) throw new Error('Network response was not ok');
        customers = await response.json();
        originalCustomers = [...customers];
        renderCustomerTable(customers);
        document.getElementById('customer-error').classList.add('hidden');
    } catch (error) {
        console.error('Error fetching customers:', error);
        document.getElementById('customer-error').classList.remove('hidden');
    }
}

// Render customer table
function renderCustomerTable(data) {
    const tbody = document.getElementById('customer-table-body');
    tbody.innerHTML = '';
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="p-2 text-center text-gray-600">No customers found</td></tr>';
        return;
    }
    data.forEach(customer => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="p-2 border"><input type="checkbox" class="customer-checkbox" data-id="${customer.customer_id}"></td>
            <td class="p-2 border">${customer.customer_id}</td>
            <td class="p-2 border">${customer.loyalty}</td>
            <td class="p-2 border">${customer.churn_probability}</td>
        `;
        tbody.appendChild(row);

        // Add click event to row to toggle checkbox
        row.addEventListener('click', (e) => {
            // Avoid toggling if the checkbox itself or a sorting header is clicked
            if (e.target.type === 'checkbox' || e.target.tagName === 'TH') return;
            const checkbox = row.querySelector('.customer-checkbox');
            checkbox.checked = !checkbox.checked;
            updateSendOfferButton();
        });

        // Add change event to checkbox
        const checkbox = row.querySelector('.customer-checkbox');
        checkbox.addEventListener('change', () => {
            updateSendOfferButton();
        });
    });
    updateSendOfferButton();
}

// Sorting
document.querySelectorAll('#customer-table th.cursor-pointer').forEach(th => {
    th.addEventListener('click', () => {
        const key = th.dataset.sort;
        const isAsc = th.classList.toggle('asc');
        customers.sort((a, b) => {
            let valA = a[key];
            let valB = b[key];
            if (key === 'loyalty') {
                const loyaltyOrder = { Low: 1, Medium: 2, High: 3 };
                valA = loyaltyOrder[valA];
                valB = loyaltyOrder[valB];
            } else if (key === 'name') {
                return isAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
            }
            return isAsc ? valA - valB : valB - valA;
        });
        renderCustomerTable(customers);
    });
});

// Filtering
document.getElementById('apply-filters').addEventListener('click', () => {
    const churnFilter = parseFloat(document.getElementById('churn-filter').value) || 0;
    const loyaltyFilter = document.getElementById('loyalty-filter').value;

    // Validate churn filter
    if (churnFilter < 0 || churnFilter > 100) {
        alert('Churn probability must be between 0 and 100');
        return;
    }

    customers = originalCustomers.filter(customer => {
        const churnMatch = customer.churn_probability >= churnFilter;
        const loyaltyMatch = loyaltyFilter === 'all' || customer.loyalty === loyaltyFilter;
        return churnMatch && loyaltyMatch;
    });
    renderCustomerTable(customers);
});

// Select All Checkbox
document.getElementById('select-all').addEventListener('change', (e) => {
    document.querySelectorAll('.customer-checkbox').forEach(checkbox => {
        checkbox.checked = e.target.checked;
    });
    updateSendOfferButton();
});

// Update Send Offer Button
function updateSendOfferButton() {
    const selected = document.querySelectorAll('.customer-checkbox:checked').length;
    const button = document.getElementById('send-offer');
    button.disabled = selected === 0;
    button.textContent = selected > 0 ? `Send Offer (${selected} selected)` : 'Send Offer';
}

// Send Offer
document.getElementById('send-offer').addEventListener('click', async () => {
    const selectedIds = Array.from(document.querySelectorAll('.customer-checkbox:checked')).map(cb => cb.dataset.id);
    if (selectedIds.length === 0) {
        alert('Please select at least one customer');
        return;
    }

    try {
        const response = await fetch('/api/send-offer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ customer_ids: selectedIds })
        });
        const result = await response.json();
        console.log(result)
        if (response.ok) {
            console.log("send it",result)
            alert(result.message || 'Offers sent successfully!');
            document.querySelectorAll('.customer-checkbox').forEach(cb => cb.checked = false);
            document.getElementById('select-all').checked = false;
            updateSendOfferButton();
        } else {
            alert(result.message || 'Failed to send offers.');
        }
    } catch (error) {
        console.error('Error sending offers:', error);
        alert('Error sending offers. Please try again.');
    }
});

// Topic Modeling Data Handling
async function fetchTopics() {
    try {
        const response = await fetch('/api/topics');
        if (!response.ok) throw new Error('Network response was not ok');
        const topics = await response.json();
        renderTopics(topics);
        document.getElementById('topics-error').classList.add('hidden');
    } catch (error) {
        console.error('Error fetching topics:', error);
        document.getElementById('topics-error').classList.remove('hidden');
    }
}

function renderTopics(topics) {
    const container = document.getElementById('topics-list');
    container.innerHTML = '';
    if (topics.length === 0) {
        container.innerHTML = '<p class="text-gray-600">No topics found</p>';
        return;
    }
    topics.forEach(topic => {
        console.log(topic.frequency)
        const card = document.createElement('div');
        card.className = 'topic-card';
        card.innerHTML = `
            <h3 class="text-lg font-semibold text-gray-800">${topic.topic_name}</h3>
            <p class="text-gray-600">${topic.description}</p>
        `;
        container.appendChild(card);
    });
}
// <p class="text-sm text-gray-500 mt-2">Frequency: ${topic.frequency}</p>
// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initTableau();
    fetchCustomers();
    fetchTopics();
});