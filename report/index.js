const fetch = require("node-fetch");
const { Storage } = require("@google-cloud/storage");
const { CanvasRenderService } = require("chartjs-node-canvas");

const storage = new Storage();

const SLACK_URL =
  "https://hooks.slack.com/services/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";

async function createChart(game) {
  const configuration = {
    type: "line", // for line chart
    data: {
      labels: Object.keys(game),
      datasets: [
        {
          label: "Game Eval",
          data: Object.entries(game),
          fill: false,
          borderColor: ["rgba(255, 99, 132, 1)"],
          borderWidth: 1,
        },
      ],
    },
  };

  const dataUrl = await canvasRenderService.renderToDataURL(configuration); // converts chart to image
  return dataUrl;
}

exports.generateReport = async (file, context) => {
  console.log(`  Bucket: ${file.bucket}`);
  console.log(`  File: ${file.name}`);
  const buffer = await storage.bucket(file.bucket).file(file.name).download();
  const game = JSON.parse(buffer.toString("utf-9"));
  new CanvasRenderService(1000, 1000, (chart) => {
    console.log("chart built");
    const imgUrl = createChart(game);
    fetch(SLACK_URL, {
      method: "POST",
      body: JSON.stringify({
        type: "mrkdwn",
        text: "Chess game",
        attachments: [
          {
            title_link: imgUrl,
            text: "Your document: <file name>",
          },
        ],
      }),
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    });
  });
};
// [END functions_helloworld_storage]
