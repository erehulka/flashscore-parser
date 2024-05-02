CREATE TABLE IF NOT EXISTS leagues (
  id INTEGER PRIMARY KEY UNIQUE,
  country VARCHAR,
  name VARCHAR,
  urlName VARCHAR UNIQUE
);

CREATE TABLE IF NOT EXISTS teams (
  id VARCHAR PRIMARY KEY UNIQUE,
  country VARCHAR,
  name VARCHAR,
  urlName VARCHAR UNIQUE
);

CREATE TABLE IF NOT EXISTS teamMatchStats (
  id INTEGER PRIMARY KEY UNIQUE,
  team VARCHAR,
  goals INTEGER NOT NULL,
  expectedGoals FLOAT,
  ballPossession FLOAT,
  shotsTotal INTEGER,
  shotsOnGoal INTEGER,
  freeKicks INTEGER,
  corners INTEGER,
  offsides INTEGER,
  goalieSaves INTEGER,
  fouls INTEGER,
  yellowCards INTEGER,
  redCards INTEGER,
  passes INTEGER,
  attacks INTEGER,
  dangerousAttacks INTEGER,
  FOREIGN KEY (team) REFERENCES teams(id)
);

CREATE TABLE IF NOT EXISTS matches (
  id INTEGER PRIMARY KEY UNIQUE,
  leagueId INTEGER,
  homeTeam VARCHAR,
  awayTeam VARCHAR,
  dateTime VARCHAR,
  FOREIGN KEY (leagueId) REFERENCES leagues(id),
  FOREIGN KEY (homeTeam) REFERENCES teamMatchStats(id),
  FOREIGN KEY (awayTeam) REFERENCES teamMatchStats(id)
);

