import { test, expect } from '@playwright/test';

test('home page renders a usable shell without live services', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Vista Flare', { exact: true }).first()).toBeVisible();
  await expect(page.getByRole('button', { name: /toggle navigation menu/i })).toBeVisible();
});
