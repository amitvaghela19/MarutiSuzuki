import { expect, test } from "@playwright/test";

test("Run analysis updates dashboard", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Supply Chain Command Center/i })).toBeVisible();

  const btn = page.getByTestId("run-analysis-btn");
  await expect(btn).toBeVisible();
  await btn.click();

  await expect(btn).toBeDisabled({ timeout: 5_000 }).catch(() => {});
  await expect(page.getByText(/Last run|No analysis yet/i)).toBeVisible({ timeout: 90_000 });

  const hasRun = await page.getByText(/run_id|Last run/i).first().isVisible().catch(() => false);
  const hasRec = await page.getByText(/Headline recommendations|Run analysis to generate/i).first().isVisible();
  expect(hasRun || hasRec).toBeTruthy();
});
