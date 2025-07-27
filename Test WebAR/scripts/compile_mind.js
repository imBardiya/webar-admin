const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");

const imagePath = process.argv[2];
const targetId = process.argv[3];
const outputPath = path.join("static/uploads", `${targetId}.mind`);

(async () => {
  const browser = await puppeteer.launch({ headless: "new", args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.goto("https://hiuk.im/mind-ar-js/tools/image-target-tool/");
  
  const input = await page.waitForSelector('input[type="file"]');
  await input.uploadFile(imagePath);

  await page.waitForTimeout(5000);

  const downloadLink = await page.$('a[download]');
  const fileUrl = await page.evaluate(a => a.href, downloadLink);
  const viewSource = await page.goto(fileUrl);
  const buffer = await viewSource.buffer();

  fs.writeFileSync(outputPath, buffer);
  await browser.close();
})();
