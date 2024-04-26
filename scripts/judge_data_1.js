const puppeteer = require('puppeteer');
const ExcelJS = require('exceljs');

async function navigateToEventPage(page, link) {
  try {
    await page.goto(link, { waitUntil: 'domcontentloaded', timeout: 30000 });
    console.log(`Successfully navigated to: ${link}`);
    return true;
  } catch (error) {
    console.log(`Navigation failed for ${link}:`, error.message);
    return false;
  }
}

async function collectList2Links(page, link) {
  await navigateToEventPage(page, link);
  const list2Links = await page.evaluate(() => {
    const links = [];
    const list2Elements = document.querySelectorAll('.list2 a');
    list2Elements.forEach(element => {
      links.push(element.href);
    });
    return links;
  });
  console.log(`Collected ${list2Links.length} 'list2' links from: ${link}`);
  return list2Links;
}

async function scrapeData(page, link) {
  const data = await page.evaluate(() => {
    const data = [];
    const eventTitleElement = document.querySelector('.decision-top2 b a');
    const eventTitle = eventTitleElement ? eventTitleElement.textContent : 'Title not found';
    const eventDateLocationElement = document.querySelector('.decision-top2');
    const eventDateLocation = eventDateLocationElement ? eventDateLocationElement.textContent.replace(eventTitle, '').trim() : 'Date/Location not found';

    const judgeTables = Array.from(document.querySelectorAll('td > table'));

    judgeTables.forEach((table) => {
      const judgeElement = table.querySelector('.judge a');
      const judgeName = judgeElement ? judgeElement.textContent : 'Judge not found';
      const fighterNames = Array.from(table.querySelectorAll('.top-cell b')).map(fighter => fighter.textContent);
      const fighter1Name = fighterNames.length > 0 ? fighterNames[0] : 'Fighter 1 not found';
      const fighter2Name = fighterNames.length > 1 ? fighterNames[1] : 'Fighter 2 not found';

      const scores = Array.from(table.querySelectorAll('.decision')).map((row, index) => ({
        round: index + 1,
        fighter1Score: row.children[1] ? row.children[1].textContent : 'Score not found',
        fighter2Score: row.children[2] ? row.children[2].textContent : 'Score not found',
      }));

      scores.forEach(score => {
        data.push({
          eventTitle,
          eventDateLocation,
          judgeName,
          fighter1Name,
          fighter2Name,
          round: score.round,
          fighter1Score: score.fighter1Score,
          fighter2Score: score.fighter2Score,
        });
      });
    });

    return data;
  });

  return data;
}

async function navigateAndCollectList2Links(headless = true) {
  const browser = await puppeteer.launch({ headless: headless, timeout: 0 });
  const page = await browser.newPage();
  await page.goto('http://mmadecisions.com/decisions-by-event/2024/', { timeout: 30000 });

  const workbook = new ExcelJS.Workbook();
  const worksheet = workbook.addWorksheet('Scraped Data');

  worksheet.columns = [
    { header: 'Event Title', key: 'eventTitle', width: 30 },
    { header: 'Event Date and Location', key: 'eventDateLocation', width: 30 },
    { header: 'Judge Name', key: 'judgeName', width: 20 },
    { header: 'Fighter 1 Name', key: 'fighter1Name', width: 20 },
    { header: 'Fighter 2 Name', key: 'fighter2Name', width: 20 },
    { header: 'Round', key: 'round', width: 10 },
    { header: 'Fighter 1 Score', key: 'fighter1Score', width: 15 },
    { header: 'Fighter 2 Score', key: 'fighter2Score', width: 15 },
  ];

  await page.waitForSelector('.decision');
  const decisionLinks = await page.evaluate(() => {
    const links = [];
    const decisionElements = document.querySelectorAll('.decision');
    decisionElements.forEach(decision => {
      const link = decision.querySelector('a').href;
      links.push(link);
    });
    return links;
  });

  for (const link of decisionLinks) {
    const list2Links = await collectList2Links(page, link);
    for (const list2Link of list2Links) {
      console.log('Navigating to:', list2Link);
      const success = await navigateToEventPage(page, list2Link);
      if (success) {
        const fightData = await scrapeData(page, list2Link);
        fightData.forEach(fight => {
          worksheet.addRow(fight);
        });
      }
    }
  }

  await workbook.xlsx.writeFile('/Users/danielbrown/Desktop/mma_2025.xlsx');
  await browser.close();
}

navigateAndCollectList2Links(true);
