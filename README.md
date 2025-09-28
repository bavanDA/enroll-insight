# Enroll Insight

A voice course advisor for NJIT computer science students. You talk to it, it asks about your year, when you like to take classes and what you want to work on after graduating, then it recommends courses and reads the answer back to you.

We built it in 24 hours at a hackathon. Course registration is a lot of small text, tables and clicking, which is hard for students with visual, motor or learning disabilities, so everything here works by voice.

## How it works

1. The browser records your voice and sends it to the server. Azure Speech turns it into text.
2. The server keeps the conversation for your session and asks the follow up questions it still needs.
3. Gemini picks courses from NJIT's BS in Computer Science curriculum and the course list we loaded into MongoDB.
4. The server tracks what it already recommended and tells Gemini to skip those. Gemini kept suggesting the same course again without it.
5. Azure Speech reads the answer out loud.

How the prompts are set up is in [Prompting.md](Prompting.md).

## Stack

React, Tailwind CSS, FastAPI, MongoDB, Azure Speech (speech to text and text to speech), Gemini.

## Run it

Setup is in [INSTALLATION.md](INSTALLATION.md). You need a Gemini API key, an Azure Speech key and MongoDB.

## Limits

- Only undergraduate computer science for now.
- No accounts, so recommendations are not saved between visits.

MIT license.
