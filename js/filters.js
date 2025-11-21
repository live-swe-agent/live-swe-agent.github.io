/**
 * Leaderboard Filtering Functionality
 */

// Filter state for each leaderboard (will be populated dynamically)
const filterState = {};

// Store dropdown instances
const tagDropdowns = {};

/**
 * Initialize filters
 */
document.addEventListener('DOMContentLoaded', () => {
    initTypeFilters();
    initTagFilters();
});

/**
 * Get all leaderboard names from embedded data
 */
function getLeaderboardNames() {
    const dataElement = document.getElementById('leaderboard-data');
    if (!dataElement) return [];

    const leaderboards = JSON.parse(dataElement.textContent);
    return leaderboards.map(lb => lb.name);
}

/**
 * Initialize type filters (Proprietary/Open Source)
 */
function initTypeFilters() {
    const leaderboards = getLeaderboardNames();

    leaderboards.forEach(leaderboard => {
        // Initialize filter state for this leaderboard
        if (!filterState[leaderboard]) {
            filterState[leaderboard] = {
                type: 'all',
                tags: new Set(['all'])
            };
        }

        const filterButtons = document.querySelectorAll(`#${leaderboard}-type-filter .filter-btn`);

        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                const filter = button.getAttribute('data-filter');

                // Update active state
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');

                // Update filter state
                filterState[leaderboard].type = filter;

                // Apply filters
                applyFilters(leaderboard);
            });
        });
    });
}

/**
 * Initialize tag filters with MultiSelectDropdown
 */
function initTagFilters() {
    // Get leaderboard tags from embedded JSON
    const tagsDataElement = document.getElementById('leaderboard-tags-data');
    if (!tagsDataElement) {
        console.error('Leaderboard tags data not found');
        return;
    }

    const leaderboardTags = JSON.parse(tagsDataElement.textContent);

    // Initialize dropdown for each leaderboard
    Object.keys(leaderboardTags).forEach(leaderboard => {
        // Initialize filter state for this leaderboard if not exists
        if (!filterState[leaderboard]) {
            filterState[leaderboard] = {
                type: 'all',
                tags: new Set(['all'])
            };
        }

        const tags = leaderboardTags[leaderboard];

        tagDropdowns[leaderboard] = new MultiSelectDropdown(`${leaderboard}-tag-filter`, {
            items: tags,
            selected: ['all'],
            displayName: 'Tags',
            searchEnabled: true,
            onSelectionChange: (selectedTags) => {
                filterState[leaderboard].tags = selectedTags;
                applyFilters(leaderboard);
            }
        });
    });
}

/**
 * Apply filters to a leaderboard
 */
function applyFilters(leaderboard) {
    const table = document.getElementById(`${leaderboard}-table`);
    const rows = table.querySelectorAll('tbody tr.leaderboard-row');
    const noResults = document.querySelector(`#${leaderboard}-content .no-results`);

    const state = filterState[leaderboard];
    let visibleCount = 0;

    rows.forEach(row => {
        let shouldShow = true;

        // Check type filter
        if (state.type !== 'all') {
            const rowType = row.getAttribute('data-type');
            if (rowType !== state.type) {
                shouldShow = false;
            }
        }

        // Check tag filter
        if (shouldShow && !state.tags.has('all')) {
            const rowTagsStr = row.getAttribute('data-tags');
            const rowTags = rowTagsStr ? rowTagsStr.split(',') : [];

            // Row must have at least one selected tag
            const hasMatchingTag = rowTags.some(tag => state.tags.has(tag));
            if (!hasMatchingTag) {
                shouldShow = false;
            }
        }

        // Update row visibility
        if (shouldShow) {
            row.classList.remove('hidden');
            visibleCount++;
        } else {
            row.classList.add('hidden');
        }
    });

    // Show/hide no results message
    if (visibleCount === 0) {
        noResults.style.display = 'block';
        table.parentElement.style.display = 'none';
    } else {
        noResults.style.display = 'none';
        table.parentElement.style.display = 'block';
    }

    // Update rankings after filtering
    if (window.leaderboard) {
        window.leaderboard.updateRankings(leaderboard);
    }

    // Update footnotes after filtering
    if (window.footnotes) {
        window.footnotes.updateFootnotes(leaderboard);
    }
}

/**
 * Reset filters for a leaderboard
 */
function resetFilters(leaderboard) {
    // Reset type filter
    const typeButtons = document.querySelectorAll(`#${leaderboard}-type-filter .filter-btn`);
    typeButtons.forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-filter') === 'all');
    });

    // Reset tag filter
    if (tagDropdowns[leaderboard]) {
        tagDropdowns[leaderboard].setSelectedItems(['all']);
    }

    // Reset state
    filterState[leaderboard] = {
        type: 'all',
        tags: new Set(['all'])
    };

    // Apply filters
    applyFilters(leaderboard);
}

/**
 * Export functions
 */
window.filters = {
    resetFilters,
    applyFilters
};
