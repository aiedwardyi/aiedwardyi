# Profile Generator Copy and Stats Design

## Goal

Make the daily profile rebuild preserve the corrected abstract and stop publishing an unreliable lifetime contribution total, while retaining the current streak and trailing-year activity chart.

## Root Cause

The scheduled `update-profile.yml` workflow regenerates the SVG assets from Python templates each day. `scripts/profile_render.py` still contains the old abstract, so every scheduled run restores it.

The generator also labels a computed number as contributions “since 2018.” It builds that number by summing annual GitHub GraphQL contribution calendars using the workflow’s repository-scoped `GITHUB_TOKEN`. That token does not provide the `read:user` access needed to include all private and internal contributions. The resulting lifetime number is therefore incomplete and must not be presented as an authoritative total.

## Chosen Design

### Hero copy

The hero template will retain its existing first abstract line:

> Building systems where agents ship real work into production.

Its second line will be:

> 9 years leading client delivery and dev teams.

The old “90-dev org shipping 200+ products” copy must not remain in the renderer, generated assets, or tests.

### Hero stats

The contribution counter will be removed completely:

- Remove the `CONTRIBUTIONS` heading.
- Remove the lifetime number.
- Remove the `since 2018` caption.
- Keep the vertical divider between the abstract and stats panel.
- Keep the `DAY STREAK` heading, value, `d` suffix, and `current` caption.
- Center the streak block within the existing right-hand panel so the layout does not leave an obvious empty first column.

### Data flow

The generator will no longer fetch account creation time or iterate through annual contribution windows. It will make one trailing-365-day contribution-calendar request, which remains the source for:

- current streak;
- weekly activity totals;
- activity chart start date.

The profile data returned by `fetch_full_profile` will no longer include `total_contributions` or `created_at`. `scripts/generate_profile.py` and `render_hero` will no longer accept or pass those values.

This removes the inaccurate metric at its source and reduces the daily workflow from multiple annual API calls to one contribution-calendar call.

## Failure Behavior

Existing request and GraphQL error handling remains unchanged: HTTP failures and GraphQL errors stop generation rather than publishing invented or stale metrics. No fallback lifetime count will be displayed.

## Testing

Renderer tests will verify that:

- the corrected abstract appears in rendered light and dark heroes;
- the old abstract does not appear;
- contribution-counter labels and values are absent;
- the streak label, value, suffix, and current caption remain;
- rendered hero output is valid XML.

Data-layer tests will verify that `fetch_full_profile`:

- performs only the trailing-365-day contribution query;
- does not fetch account creation time or annual lifetime windows;
- returns the fields required by the streak and activity renderers;
- preserves the existing streak and weekly aggregation behavior.

Generator-level coverage will verify that both hero themes use the simplified `render_hero` interface and that the generated activity chart remains present.

## Scope

The change is limited to the profile generator, its tests, and regenerated SVG assets. The README structure, activity-chart design, schedule, commit identity, and unrelated workflows remain unchanged.
