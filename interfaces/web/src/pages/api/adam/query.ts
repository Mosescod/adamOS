
import type { NextApiRequest, NextApiResponse } from 'next';
import { AdamAI } from "adamAIOS/interfaces/web/src/pages/api/adam/query";

const adam = new AdamAI();

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { message, mood } = req.body;
  const response = adam.query(message, mood);
  
  res.status(200).json({
    response: response.text,
    mood: response.mood,
    gesture: response.gesture
  });
}