CREATE TABLE IF NOT EXISTS leagues (
  id INTEGER PRIMARY KEY UNIQUE,
  country VARCHAR,
  name VARCHAR,
  urlName VARCHAR UNIQUE
);

CREATE TABLE IF NOT EXISTS teams (
  id INTEGER PRIMARY KEY UNIQUE,
  country VARCHAR,
  name VARCHAR,
  urlName VARCHAR UNIQUE
);

CREATE TABLE IF NOT EXISTS teamMatchStats (
  id INTEGER PRIMARY KEY UNIQUE,
  team INTEGER,
  goals INTEGER NOT NULL,
  expectedGoals FLOAT,
  ballPossession FLOAT,
  shotsTotal INTEGER,
  shotsOnGoal INTEGER,
  freeKicks INTEGER,
  corners INTEGER,
  offsides INTEGER,
  throwIns INTEGER,
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
  id VARCHAR PRIMARY KEY UNIQUE,
  leagueId INTEGER,
  homeTeam INTEGER,
  awayTeam INTEGER,
  FOREIGN KEY (leagueId) REFERENCES leagues(id),
  FOREIGN KEY (homeTeam) REFERENCES teams(id),
  FOREIGN KEY (awayTeam) REFERENCES teams(id)
);

