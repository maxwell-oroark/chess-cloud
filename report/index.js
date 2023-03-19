import fetch from "node-fetch";
import { Storage } from "@google-cloud/storage";
import { ChartJSNodeCanvas } from "chartjs-node-canvas";
const storage = new Storage();

/**
 * Generic background Cloud Function to be triggered by Cloud Storage.
 * This sample works for all Cloud Storage CRUD operations.
 *
 * @param {object} file The Cloud Storage file metadata.
 * @param {object} context The event metadata.
 */

const SLACK_URL = process.env.SLACK_URL;

async function createChart(analysis, chartService) {
  const moves = analysis["analysis"];
  const title = `${analysis["white_player"]} (${analysis["white_rating"]}) vs. ${analysis["black_player"]} (${analysis["black_rating"]})`;
  const configuration = {
    type: "line",
    options: {
      plugins: {
        customCanvasBackgroundColor: {
          color: "#d6d6d6",
        },
      },
      scales: {
        y: {
          suggestedMin: -1000,
          suggestedMax: 1000,
          grid: {
            color: (context) => {
              const line = context.tick.value;
              const lineColor = line === 0 ? "#666" : "#ccc";
              return lineColor;
            },
            lineWidth: (context) => {
              const line = context.tick.value;
              const lineColor = line === 0 ? 2 : 1;
              return lineColor;
            },
          },
        },
      },
    },
    data: {
      labels: moves.map((move) => move.move),
      datasets: [
        {
          label: title,
          data: moves.map((move) => move.score),
          fill: false,
          borderColor: ["rgba(255, 99, 132, 1)"],
          borderWidth: 1,
        },
      ],
    },
    plugins: [
      {
        id: "customCanvasBackgroundColor",
        beforeDraw: (chart, args, options) => {
          // background color
          const {
            ctx,
            width,
            height,
            chartArea,
            scales: { y },
          } = chart;
          ctx.save();
          ctx.globalCompositeOperation = "destination-over";
          // save entire chart canvas as white
          ctx.fillStyle = "#fff";
          ctx.fillRect(0, 0, width, height);
          // layer background negative y-axis gray
          ctx.fillStyle = options.color || "#d3d3d3";
          ctx.fillRect(
            chartArea.left,
            y.getPixelForValue(0),
            chartArea.width,
            chartArea.bottom - y.getPixelForValue(0)
          );
          ctx.restore();
        },
      },
    ],
  };

  const image = await chartService.renderToBuffer(configuration); // converts chart to image
  return image;
}

async function generateReport(file, context) {
  console.log(`  Event: ${context.eventId}`);
  console.log(`  Event Type: ${context.eventType}`);
  console.log(`  Bucket: ${file.bucket}`);
  console.log(`  File: ${file.name}`);
  console.log(`  Metageneration: ${file.metageneration}`);
  console.log(`  Created: ${file.timeCreated}`);
  console.log(`  Updated: ${file.updated}`);
  const destinationBucket = "processed_chart_images";
  const buffer = await storage.bucket(file.bucket).file(file.name).download(); //stream is created
  const analysis = JSON.parse(buffer[0].toString("utf-8"));
  const chartService = new ChartJSNodeCanvas({
    width: 1000,
    height: 1000,
  });

  const id = file.name.split(".")[0];
  const image = await createChart(analysis, chartService);
  await storage.bucket(destinationBucket).file(`${id}.png`).save(image);

  const publicUrl = `https://storage.googleapis.com/${destinationBucket}/${id}.png`;

  fetch(SLACK_URL, {
    method: "POST",
    body: JSON.stringify({
      type: "mrkdwn",
      text: `${analysis["winner"].includes("white") ? "👑" : ""} ${
        analysis["white_player"]
      } (${analysis["white_rating"]}) vs. ${
        analysis["winner"].includes("black") ? "👑" : ""
      } ${analysis["black_player"]} (${analysis["black_rating"]})`,
      attachments: [
        {
          type: "image",
          title: {
            type: "plain_text",
            text: "analyzed chess chart",
          },
          image_url: publicUrl,
          alt_text: "analysis of chess game depicted by line chart",
        },
      ],
    }),
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
  });
}

export { generateReport };
// [END functions_helloworld_storage]
