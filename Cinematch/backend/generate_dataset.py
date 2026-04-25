"""
generate_dataset.py
====================
Generates a realistic MovieLens-format dataset with:
  - 500 real, well-known movie titles with accurate genres
  - 10,000 synthetic user ratings (600 users)
  - Proper statistical distribution (not uniform random)

Run: python generate_dataset.py
Output: data/movies.csv, data/ratings.csv
"""

import pandas as pd
import numpy as np
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

np.random.seed(42)

# =============================================================================
# 500 REAL MOVIE TITLES WITH ACCURATE GENRES
# Format: (movieId, title, genres)
# Genres match MovieLens format (pipe-separated)
# =============================================================================

MOVIES = [
    # ── ACTION ────────────────────────────────────────────────────────────────
    (1,   "Die Hard (1988)",                         "Action|Thriller"),
    (2,   "Mad Max: Fury Road (2015)",               "Action|Adventure|Sci-Fi|Thriller"),
    (3,   "The Dark Knight (2008)",                  "Action|Crime|Drama|Thriller"),
    (4,   "Inception (2010)",                        "Action|Adventure|Sci-Fi|Thriller"),
    (5,   "John Wick (2014)",                        "Action|Crime|Thriller"),
    (6,   "Mission: Impossible - Fallout (2018)",    "Action|Adventure|Thriller"),
    (7,   "The Avengers (2012)",                     "Action|Adventure|Sci-Fi"),
    (8,   "Gladiator (2000)",                        "Action|Adventure|Drama"),
    (9,   "The Matrix (1999)",                       "Action|Sci-Fi"),
    (10,  "Speed (1994)",                            "Action|Crime|Thriller"),
    (11,  "Top Gun: Maverick (2022)",                "Action|Drama"),
    (12,  "Black Panther (2018)",                    "Action|Adventure|Sci-Fi"),
    (13,  "Iron Man (2008)",                         "Action|Adventure|Sci-Fi"),
    (14,  "Captain America: Civil War (2016)",       "Action|Adventure|Sci-Fi"),
    (15,  "The Raid: Redemption (2011)",             "Action|Crime|Thriller"),
    (16,  "Heat (1995)",                             "Action|Crime|Drama|Thriller"),
    (17,  "Terminator 2: Judgment Day (1991)",       "Action|Sci-Fi|Thriller"),
    (18,  "RoboCop (1987)",                          "Action|Crime|Sci-Fi|Thriller"),
    (19,  "Lethal Weapon (1987)",                    "Action|Comedy|Crime|Thriller"),
    (20,  "Point Break (1991)",                      "Action|Crime|Thriller"),

    # ── ADVENTURE ─────────────────────────────────────────────────────────────
    (21,  "Indiana Jones and the Raiders of the Lost Ark (1981)", "Action|Adventure"),
    (22,  "The Lord of the Rings: The Fellowship of the Ring (2001)", "Adventure|Fantasy"),
    (23,  "Pirates of the Caribbean: The Curse of the Black Pearl (2003)", "Action|Adventure|Fantasy"),
    (24,  "Jurassic Park (1993)",                    "Action|Adventure|Sci-Fi|Thriller"),
    (25,  "The Revenant (2015)",                     "Adventure|Drama|Thriller"),
    (26,  "Into the Wild (2007)",                    "Adventure|Biography|Drama"),
    (27,  "Cast Away (2000)",                        "Adventure|Drama"),
    (28,  "The Martian (2015)",                      "Adventure|Drama|Sci-Fi"),
    (29,  "Interstellar (2014)",                     "Adventure|Drama|Sci-Fi"),
    (30,  "Avatar (2009)",                           "Action|Adventure|Fantasy|Sci-Fi"),
    (31,  "Dune (2021)",                             "Adventure|Drama|Sci-Fi"),
    (32,  "The Princess Bride (1987)",               "Adventure|Comedy|Fantasy|Romance"),
    (33,  "Treasure Planet (2002)",                  "Adventure|Animation|Fantasy|Sci-Fi"),
    (34,  "National Treasure (2004)",                "Action|Adventure|Mystery|Thriller"),
    (35,  "Romancing the Stone (1984)",              "Action|Adventure|Comedy|Romance"),

    # ── ANIMATION ─────────────────────────────────────────────────────────────
    (36,  "Toy Story (1995)",                        "Adventure|Animation|Children|Comedy|Fantasy"),
    (37,  "The Lion King (1994)",                    "Adventure|Animation|Children|Drama|Musical"),
    (38,  "Spirited Away (2001)",                    "Adventure|Animation|Children|Fantasy|Mystery"),
    (39,  "Finding Nemo (2003)",                     "Adventure|Animation|Children|Comedy"),
    (40,  "WALL-E (2008)",                           "Adventure|Animation|Children|Romance|Sci-Fi"),
    (41,  "Up (2009)",                               "Adventure|Animation|Children|Comedy|Drama"),
    (42,  "Inside Out (2015)",                       "Adventure|Animation|Children|Comedy|Drama"),
    (43,  "Coco (2017)",                             "Adventure|Animation|Children|Comedy|Fantasy|Musical"),
    (44,  "Howl's Moving Castle (2004)",             "Adventure|Animation|Children|Fantasy|Romance"),
    (45,  "My Neighbor Totoro (1988)",               "Adventure|Animation|Children|Fantasy"),
    (46,  "Shrek (2001)",                            "Adventure|Animation|Children|Comedy|Fantasy|Romance"),
    (47,  "Kung Fu Panda (2008)",                    "Action|Adventure|Animation|Children|Comedy"),
    (48,  "Zootopia (2016)",                         "Adventure|Animation|Children|Comedy|Mystery"),
    (49,  "The Incredibles (2004)",                  "Action|Adventure|Animation|Children|Comedy"),
    (50,  "Moana (2016)",                            "Adventure|Animation|Children|Comedy|Fantasy|Musical"),
    (51,  "Frozen (2013)",                           "Adventure|Animation|Children|Comedy|Fantasy|Musical|Romance"),
    (52,  "Ratatouille (2007)",                      "Adventure|Animation|Children|Comedy|Drama"),
    (53,  "Princess Mononoke (1997)",                "Action|Adventure|Animation|Drama|Fantasy"),
    (54,  "Akira (1988)",                            "Action|Animation|Drama|Sci-Fi|Thriller"),
    (55,  "Ghost in the Shell (1995)",               "Animation|Drama|Sci-Fi|Thriller"),

    # ── COMEDY ────────────────────────────────────────────────────────────────
    (56,  "The Grand Budapest Hotel (2014)",         "Comedy|Crime|Drama"),
    (57,  "Superbad (2007)",                         "Comedy"),
    (58,  "Bridesmaids (2011)",                      "Comedy|Romance"),
    (59,  "The Hangover (2009)",                     "Comedy"),
    (60,  "Groundhog Day (1993)",                    "Comedy|Fantasy|Romance"),
    (61,  "Home Alone (1990)",                       "Children|Comedy"),
    (62,  "Mrs. Doubtfire (1993)",                   "Comedy|Drama"),
    (63,  "Ferris Bueller's Day Off (1986)",         "Comedy"),
    (64,  "The Big Lebowski (1998)",                 "Comedy|Crime"),
    (65,  "Office Space (1999)",                     "Comedy"),
    (66,  "Anchorman (2004)",                        "Comedy"),
    (67,  "Mean Girls (2004)",                       "Comedy"),
    (68,  "Legally Blonde (2001)",                   "Comedy|Romance"),
    (69,  "Crazy Rich Asians (2018)",                "Comedy|Drama|Romance"),
    (70,  "The 40-Year-Old Virgin (2005)",           "Comedy|Romance"),
    (71,  "Knocked Up (2007)",                       "Comedy|Drama|Romance"),
    (72,  "American Pie (1999)",                     "Comedy|Romance"),
    (73,  "There's Something About Mary (1998)",     "Comedy|Romance"),
    (74,  "Monty Python and the Holy Grail (1975)",  "Adventure|Comedy|Fantasy"),
    (75,  "Airplane! (1980)",                        "Comedy"),

    # ── CRIME / THRILLER ──────────────────────────────────────────────────────
    (76,  "The Godfather (1972)",                    "Crime|Drama"),
    (77,  "Pulp Fiction (1994)",                     "Crime|Drama|Thriller"),
    (78,  "No Country for Old Men (2007)",           "Crime|Drama|Thriller"),
    (79,  "Fargo (1996)",                            "Crime|Drama|Thriller"),
    (80,  "Se7en (1995)",                            "Crime|Drama|Mystery|Thriller"),
    (81,  "Zodiac (2007)",                           "Crime|Drama|Mystery|Thriller"),
    (82,  "L.A. Confidential (1997)",                "Crime|Drama|Mystery|Thriller"),
    (83,  "The Silence of the Lambs (1991)",         "Crime|Drama|Horror|Thriller"),
    (84,  "Goodfellas (1990)",                       "Crime|Drama"),
    (85,  "The Departed (2006)",                     "Crime|Drama|Thriller"),
    (86,  "American Gangster (2007)",                "Biography|Crime|Drama"),
    (87,  "Drive (2011)",                            "Crime|Drama|Thriller"),
    (88,  "Prisoners (2013)",                        "Crime|Drama|Mystery|Thriller"),
    (89,  "Gone Girl (2014)",                        "Drama|Mystery|Thriller"),
    (90,  "Knives Out (2019)",                       "Comedy|Crime|Drama|Mystery|Thriller"),
    (91,  "Ocean's Eleven (2001)",                   "Crime|Thriller"),
    (92,  "Catch Me If You Can (2002)",              "Biography|Crime|Drama|Thriller"),
    (93,  "The Usual Suspects (1995)",               "Crime|Drama|Mystery|Thriller"),
    (94,  "Chinatown (1974)",                        "Crime|Drama|Mystery|Thriller"),
    (95,  "Heat (1995)",                             "Action|Crime|Drama|Thriller"),

    # ── DRAMA ─────────────────────────────────────────────────────────────────
    (96,  "The Shawshank Redemption (1994)",         "Drama"),
    (97,  "Schindler's List (1993)",                 "Biography|Drama|History"),
    (98,  "Forrest Gump (1994)",                     "Comedy|Drama|Romance"),
    (99,  "Good Will Hunting (1997)",                "Drama|Romance"),
    (100, "A Beautiful Mind (2001)",                 "Biography|Drama|Mystery"),
    (101, "The Green Mile (1999)",                   "Crime|Drama|Fantasy|Mystery"),
    (102, "Whiplash (2014)",                         "Drama|Music"),
    (103, "Black Swan (2010)",                       "Drama|Horror|Mystery|Thriller"),
    (104, "Marriage Story (2019)",                   "Drama|Romance"),
    (105, "Parasite (2019)",                         "Crime|Drama|Thriller"),
    (106, "1917 (2019)",                             "Drama|War"),
    (107, "The Pianist (2002)",                      "Biography|Drama|War"),
    (108, "Manchester by the Sea (2016)",            "Drama"),
    (109, "Moonlight (2016)",                        "Drama"),
    (110, "Nomadland (2020)",                        "Drama"),
    (111, "Roma (2018)",                             "Drama"),
    (112, "The Irishman (2019)",                     "Biography|Crime|Drama"),
    (113, "There Will Be Blood (2007)",              "Drama|Western"),
    (114, "12 Angry Men (1957)",                     "Crime|Drama"),
    (115, "To Kill a Mockingbird (1962)",            "Crime|Drama"),

    # ── ROMANCE ───────────────────────────────────────────────────────────────
    (116, "Titanic (1997)",                          "Drama|Romance"),
    (117, "La La Land (2016)",                       "Comedy|Drama|Music|Musical|Romance"),
    (118, "Eternal Sunshine of the Spotless Mind (2004)", "Drama|Romance|Sci-Fi"),
    (119, "Before Sunrise (1995)",                   "Drama|Romance"),
    (120, "Notting Hill (1999)",                     "Comedy|Drama|Romance"),
    (121, "When Harry Met Sally (1989)",             "Comedy|Romance"),
    (122, "The Notebook (2004)",                     "Drama|Romance"),
    (123, "Pride and Prejudice (2005)",              "Drama|Romance"),
    (124, "About Time (2013)",                       "Comedy|Drama|Fantasy|Romance"),
    (125, "Crazy, Stupid, Love (2011)",              "Comedy|Drama|Romance"),
    (126, "Her (2013)",                              "Drama|Romance|Sci-Fi"),
    (127, "500 Days of Summer (2009)",               "Comedy|Drama|Romance"),
    (128, "Silver Linings Playbook (2012)",          "Comedy|Drama|Romance"),
    (129, "Atonement (2007)",                        "Drama|Romance|War"),
    (130, "Call Me by Your Name (2017)",             "Drama|Romance"),

    # ── SCI-FI ────────────────────────────────────────────────────────────────
    (131, "2001: A Space Odyssey (1968)",            "Mystery|Sci-Fi"),
    (132, "Blade Runner (1982)",                     "Sci-Fi|Thriller"),
    (133, "Blade Runner 2049 (2017)",                "Drama|Mystery|Sci-Fi|Thriller"),
    (134, "Alien (1979)",                            "Horror|Sci-Fi"),
    (135, "Aliens (1986)",                           "Action|Horror|Sci-Fi|Thriller"),
    (136, "The Thing (1982)",                        "Horror|Mystery|Sci-Fi"),
    (137, "Arrival (2016)",                          "Drama|Mystery|Sci-Fi|Thriller"),
    (138, "Annihilation (2018)",                     "Adventure|Drama|Horror|Mystery|Sci-Fi|Thriller"),
    (139, "Ex Machina (2014)",                       "Drama|Mystery|Sci-Fi|Thriller"),
    (140, "Gravity (2013)",                          "Drama|Sci-Fi|Thriller"),
    (141, "The Truman Show (1998)",                  "Comedy|Drama|Sci-Fi"),
    (142, "Eternal Sunshine of the Spotless Mind (2004)", "Drama|Romance|Sci-Fi"),
    (143, "Minority Report (2002)",                  "Action|Crime|Mystery|Sci-Fi|Thriller"),
    (144, "Looper (2012)",                           "Action|Crime|Drama|Sci-Fi|Thriller"),
    (145, "District 9 (2009)",                       "Action|Drama|Sci-Fi|Thriller"),
    (146, "Children of Men (2006)",                  "Action|Drama|Sci-Fi|Thriller"),
    (147, "E.T. the Extra-Terrestrial (1982)",       "Children|Drama|Sci-Fi"),
    (148, "Close Encounters of the Third Kind (1977)","Drama|Sci-Fi"),
    (149, "Contact (1997)",                          "Drama|Mystery|Sci-Fi"),
    (150, "Moon (2009)",                             "Drama|Mystery|Sci-Fi"),

    # ── HORROR ────────────────────────────────────────────────────────────────
    (151, "The Shining (1980)",                      "Drama|Horror|Thriller"),
    (152, "Get Out (2017)",                          "Horror|Mystery|Thriller"),
    (153, "Hereditary (2018)",                       "Drama|Horror|Mystery|Thriller"),
    (154, "A Quiet Place (2018)",                    "Drama|Horror|Sci-Fi|Thriller"),
    (155, "Midsommar (2019)",                        "Drama|Horror|Mystery|Thriller"),
    (156, "It (2017)",                               "Drama|Horror|Thriller"),
    (157, "The Witch (2015)",                        "Drama|Horror|Mystery|Thriller"),
    (158, "Psycho (1960)",                           "Horror|Mystery|Thriller"),
    (159, "Halloween (1978)",                        "Horror|Thriller"),
    (160, "A Nightmare on Elm Street (1984)",        "Fantasy|Horror|Thriller"),
    (161, "Scream (1996)",                           "Comedy|Horror|Mystery|Thriller"),
    (162, "The Conjuring (2013)",                    "Horror|Mystery|Thriller"),
    (163, "Sinister (2012)",                         "Horror|Mystery|Thriller"),
    (164, "Insidious (2010)",                        "Horror|Mystery|Thriller"),
    (165, "Train to Busan (2016)",                   "Action|Horror|Thriller"),

    # ── MYSTERY ───────────────────────────────────────────────────────────────
    (166, "Memento (2000)",                          "Mystery|Thriller"),
    (167, "The Sixth Sense (1999)",                  "Drama|Mystery|Thriller"),
    (168, "Shutter Island (2010)",                   "Drama|Mystery|Thriller"),
    (169, "Mulholland Drive (2001)",                 "Drama|Mystery|Thriller"),
    (170, "Rear Window (1954)",                      "Crime|Mystery|Thriller"),
    (171, "Vertigo (1958)",                          "Crime|Mystery|Romance|Thriller"),
    (172, "The Girl with the Dragon Tattoo (2011)",  "Crime|Drama|Mystery|Thriller"),
    (173, "Sharp Objects (2018)",                    "Drama|Mystery|Thriller"),
    (174, "Glass Onion: A Knives Out Mystery (2022)","Comedy|Crime|Mystery|Thriller"),
    (175, "The Prestige (2006)",                     "Drama|Mystery|Sci-Fi|Thriller"),

    # ── FANTASY ───────────────────────────────────────────────────────────────
    (176, "The Lord of the Rings: The Two Towers (2002)", "Adventure|Fantasy"),
    (177, "The Lord of the Rings: The Return of the King (2003)", "Adventure|Fantasy"),
    (178, "Harry Potter and the Sorcerer's Stone (2001)", "Adventure|Children|Fantasy"),
    (179, "Harry Potter and the Prisoner of Azkaban (2004)", "Adventure|Children|Fantasy|Mystery"),
    (180, "Pan's Labyrinth (2006)",                  "Drama|Fantasy|War"),
    (181, "Big Fish (2003)",                         "Drama|Fantasy|Romance"),
    (182, "Edward Scissorhands (1990)",              "Drama|Fantasy|Romance"),
    (183, "Labyrinth (1986)",                        "Adventure|Children|Fantasy|Musical"),
    (184, "The NeverEnding Story (1984)",            "Adventure|Children|Drama|Fantasy"),
    (185, "Willow (1988)",                           "Action|Adventure|Fantasy"),

    # ── DOCUMENTARY ───────────────────────────────────────────────────────────
    (186, "March of the Penguins (2005)",            "Documentary"),
    (187, "Jiro Dreams of Sushi (2011)",             "Documentary"),
    (188, "Won't You Be My Neighbor? (2018)",        "Documentary"),
    (189, "Free Solo (2018)",                        "Documentary"),
    (190, "Making a Murderer (2015)",                "Crime|Documentary"),
    (191, "13th (2016)",                             "Documentary"),
    (192, "Bowling for Columbine (2002)",            "Documentary"),
    (193, "An Inconvenient Truth (2006)",            "Documentary"),
    (194, "The Act of Killing (2012)",               "Documentary|Drama|War"),
    (195, "Exit Through the Gift Shop (2010)",       "Documentary"),

    # ── MUSICAL ───────────────────────────────────────────────────────────────
    (196, "The Sound of Music (1965)",               "Biography|Drama|Musical"),
    (197, "Singin' in the Rain (1952)",              "Comedy|Musical|Romance"),
    (198, "Chicago (2002)",                          "Comedy|Crime|Drama|Musical"),
    (199, "Grease (1978)",                           "Comedy|Musical|Romance"),
    (200, "Bohemian Rhapsody (2018)",                "Biography|Drama|Musical"),
    (201, "Rocketman (2019)",                        "Biography|Drama|Musical|Romance"),
    (202, "Mamma Mia! (2008)",                       "Comedy|Drama|Musical|Romance"),
    (203, "Les Misérables (2012)",                   "Drama|History|Musical|Romance|War"),
    (204, "Into the Woods (2014)",                   "Adventure|Drama|Fantasy|Musical"),
    (205, "Moulin Rouge! (2001)",                    "Drama|Musical|Romance|Thriller"),

    # ── BIOGRAPHY / HISTORY ───────────────────────────────────────────────────
    (206, "Lincoln (2012)",                          "Biography|Drama|History"),
    (207, "The Social Network (2010)",               "Biography|Drama"),
    (208, "Bohemian Rhapsody (2018)",                "Biography|Drama|Musical"),
    (209, "The Theory of Everything (2014)",         "Biography|Drama|Romance"),
    (210, "Darkest Hour (2017)",                     "Biography|Drama|History|War"),
    (211, "Selma (2014)",                            "Biography|Drama|History"),
    (212, "Erin Brockovich (2000)",                  "Biography|Crime|Drama"),
    (213, "The Imitation Game (2014)",               "Biography|Drama|History|Mystery|Thriller|War"),
    (214, "Rush (2013)",                             "Biography|Drama|Sport"),
    (215, "Sully (2016)",                            "Biography|Drama"),

    # ── WAR ───────────────────────────────────────────────────────────────────
    (216, "Saving Private Ryan (1998)",              "Action|Drama|War"),
    (217, "Full Metal Jacket (1987)",                "Drama|War"),
    (218, "Apocalypse Now (1979)",                   "Drama|War"),
    (219, "Platoon (1986)",                          "Drama|War"),
    (220, "The Hurt Locker (2008)",                  "Drama|Thriller|War"),
    (221, "Dunkirk (2017)",                          "Action|Drama|History|Thriller|War"),
    (222, "Hacksaw Ridge (2016)",                    "Biography|Drama|History|War"),
    (223, "Fury (2014)",                             "Action|Drama|War"),
    (224, "Midway (2019)",                           "Action|Drama|History|War"),
    (225, "Das Boot (1981)",                         "Drama|Thriller|War"),

    # ── FAMILY / CHILDREN ─────────────────────────────────────────────────────
    (226, "The Parent Trap (1998)",                  "Children|Comedy|Family|Romance"),
    (227, "Matilda (1996)",                          "Children|Comedy|Family|Fantasy"),
    (228, "Willy Wonka and the Chocolate Factory (1971)", "Children|Comedy|Family|Fantasy|Musical"),
    (229, "The Wizard of Oz (1939)",                 "Adventure|Children|Family|Fantasy|Musical"),
    (230, "Mary Poppins (1964)",                     "Children|Comedy|Family|Fantasy|Musical"),
    (231, "Babe (1995)",                             "Children|Comedy|Drama|Family"),
    (232, "Stuart Little (1999)",                    "Adventure|Children|Comedy|Family"),
    (233, "The Chronicles of Narnia (2005)",         "Adventure|Children|Family|Fantasy"),
    (234, "A Little Princess (1995)",                "Children|Drama|Family|Fantasy"),
    (235, "The Secret Garden (1993)",                "Children|Drama|Family|Fantasy"),

    # ── WESTERN ───────────────────────────────────────────────────────────────
    (236, "The Good, the Bad and the Ugly (1966)",   "Western"),
    (237, "Unforgiven (1992)",                       "Drama|Western"),
    (238, "Django Unchained (2012)",                 "Drama|Western"),
    (239, "True Grit (2010)",                        "Adventure|Drama|Western"),
    (240, "The Hateful Eight (2015)",                "Crime|Drama|Mystery|Western"),
    (241, "Once Upon a Time in the West (1968)",     "Drama|Western"),
    (242, "Dances with Wolves (1990)",               "Adventure|Drama|Western"),
    (243, "Tombstone (1993)",                        "Action|Drama|History|Western"),
    (244, "Butch Cassidy and the Sundance Kid (1969)","Action|Biography|Crime|Drama|Western"),
    (245, "The Wild Bunch (1969)",                   "Action|Adventure|Drama|Western"),

    # ── SPORT ─────────────────────────────────────────────────────────────────
    (246, "Rocky (1976)",                            "Drama|Sport"),
    (247, "Raging Bull (1980)",                      "Biography|Drama|Sport"),
    (248, "Moneyball (2011)",                        "Biography|Drama|Sport"),
    (249, "The Blind Side (2009)",                   "Biography|Drama|Family|Sport"),
    (250, "Remember the Titans (2000)",              "Biography|Drama|Family|Sport"),
    (251, "Hoosiers (1986)",                         "Drama|Sport"),
    (252, "Rudy (1993)",                             "Biography|Drama|Family|Sport"),
    (253, "Jerry Maguire (1996)",                    "Comedy|Drama|Romance|Sport"),
    (254, "Bend It Like Beckham (2002)",             "Comedy|Drama|Family|Romance|Sport"),
    (255, "The Karate Kid (1984)",                   "Action|Children|Drama|Sport"),

    # ── INTERNATIONAL (non-English) ───────────────────────────────────────────
    (256, "Parasite (2019)",                         "Comedy|Drama|Thriller"),             # Korean
    (257, "City of God (2002)",                      "Crime|Drama"),                       # Portuguese
    (258, "Pan's Labyrinth (2006)",                  "Drama|Fantasy|War"),                 # Spanish
    (259, "Amélie (2001)",                           "Comedy|Romance"),                    # French
    (260, "Cinema Paradiso (1988)",                  "Drama|Romance"),                     # Italian
    (261, "Life Is Beautiful (1997)",                "Comedy|Drama|Romance|War"),          # Italian
    (262, "Oldboy (2003)",                           "Action|Drama|Mystery|Thriller"),     # Korean
    (263, "The Secret in Their Eyes (2009)",         "Crime|Drama|Mystery|Romance|Thriller"), # Spanish
    (264, "Y Tu Mamá También (2001)",                "Drama|Romance"),                     # Spanish
    (265, "Crouching Tiger, Hidden Dragon (2000)",   "Action|Adventure|Drama|Fantasy|Romance"), # Chinese

    # ── PSYCHOLOGICAL THRILLER ────────────────────────────────────────────────
    (266, "Fight Club (1999)",                       "Drama|Mystery|Thriller"),
    (267, "American Psycho (2000)",                  "Crime|Drama|Horror|Mystery|Thriller"),
    (268, "Donnie Darko (2001)",                     "Drama|Mystery|Sci-Fi|Thriller"),
    (269, "Black Swan (2010)",                       "Drama|Horror|Mystery|Thriller"),
    (270, "The Game (1997)",                         "Drama|Mystery|Thriller"),
    (271, "Gone Girl (2014)",                        "Drama|Mystery|Thriller"),
    (272, "Uncut Gems (2019)",                       "Crime|Drama|Thriller"),
    (273, "Nightcrawler (2014)",                     "Crime|Drama|Thriller"),
    (274, "Requiem for a Dream (2000)",              "Drama"),
    (275, "Pi (1998)",                               "Drama|Mystery|Sci-Fi|Thriller"),

    # ── CLASSICS ──────────────────────────────────────────────────────────────
    (276, "Citizen Kane (1941)",                     "Drama|Mystery"),
    (277, "Casablanca (1942)",                       "Drama|Romance|War"),
    (278, "Sunset Boulevard (1950)",                 "Drama|Film-Noir"),
    (279, "Rear Window (1954)",                      "Crime|Mystery|Thriller"),
    (280, "Some Like It Hot (1959)",                 "Comedy|Romance"),
    (281, "Ben-Hur (1959)",                          "Action|Adventure|Drama|History"),
    (282, "Spartacus (1960)",                        "Action|Drama|History"),
    (283, "Lawrence of Arabia (1962)",               "Adventure|Biography|Drama|History|War"),
    (284, "Doctor Zhivago (1965)",                   "Drama|Romance|War"),
    (285, "2001: A Space Odyssey (1968)",            "Mystery|Sci-Fi"),

    # ── SUPERHERO ─────────────────────────────────────────────────────────────
    (286, "Spider-Man: Into the Spider-Verse (2018)","Action|Adventure|Animation|Sci-Fi"),
    (287, "The Dark Knight Rises (2012)",            "Action|Crime|Drama|Thriller"),
    (288, "Batman v Superman: Dawn of Justice (2016)","Action|Adventure|Sci-Fi"),
    (289, "Guardians of the Galaxy (2014)",          "Action|Adventure|Comedy|Sci-Fi"),
    (290, "Thor: Ragnarok (2017)",                   "Action|Adventure|Comedy|Sci-Fi"),
    (291, "Avengers: Infinity War (2018)",           "Action|Adventure|Sci-Fi"),
    (292, "Avengers: Endgame (2019)",                "Action|Adventure|Drama|Sci-Fi"),
    (293, "Doctor Strange (2016)",                   "Action|Adventure|Fantasy|Sci-Fi"),
    (294, "Black Widow (2021)",                      "Action|Adventure|Sci-Fi|Thriller"),
    (295, "Shang-Chi and the Legend of the Ten Rings (2021)", "Action|Adventure|Fantasy|Sci-Fi"),

    # ── INDIE / ART HOUSE ─────────────────────────────────────────────────────
    (296, "Moonlight (2016)",                        "Drama"),
    (297, "Lady Bird (2017)",                        "Comedy|Drama"),
    (298, "The Lobster (2015)",                      "Drama|Romance|Sci-Fi|Thriller"),
    (299, "Birdman (2014)",                          "Comedy|Drama|Mystery|Thriller"),
    (300, "Boyhood (2014)",                          "Drama"),
    (301, "Whiplash (2014)",                         "Drama|Music"),
    (302, "Phantom Thread (2017)",                   "Drama|Romance|Thriller"),
    (303, "The Power of the Dog (2021)",             "Drama|Western"),
    (304, "Portrait of a Lady on Fire (2019)",       "Drama|Romance"),
    (305, "Aftersun (2022)",                         "Drama"),

    # ── HEIST ─────────────────────────────────────────────────────────────────
    (306, "Ocean's Eleven (2001)",                   "Crime|Thriller"),
    (307, "The Italian Job (2003)",                  "Action|Crime|Thriller"),
    (308, "Heat (1995)",                             "Action|Crime|Drama|Thriller"),
    (309, "Rififi (1955)",                           "Crime|Drama|Film-Noir|Thriller"),
    (310, "The Town (2010)",                         "Crime|Drama|Thriller"),
    (311, "Baby Driver (2017)",                      "Action|Crime|Drama|Music|Thriller"),
    (312, "Snatch (2000)",                           "Comedy|Crime|Thriller"),
    (313, "Lock, Stock and Two Smoking Barrels (1998)","Comedy|Crime|Thriller"),
    (314, "Now You See Me (2013)",                   "Crime|Mystery|Thriller"),
    (315, "The Sting (1973)",                        "Comedy|Crime|Drama"),

    # ── COMING-OF-AGE ─────────────────────────────────────────────────────────
    (316, "The Perks of Being a Wallflower (2012)",  "Drama|Romance"),
    (317, "Stand by Me (1986)",                      "Adventure|Drama"),
    (318, "The Breakfast Club (1985)",               "Comedy|Drama|Romance"),
    (319, "Sixteen Candles (1984)",                  "Comedy|Drama|Romance"),
    (320, "Dazed and Confused (1993)",               "Comedy|Drama"),
    (321, "Almost Famous (2000)",                    "Adventure|Drama|Music|Romance"),
    (322, "Juno (2007)",                             "Comedy|Drama|Romance"),
    (323, "Little Miss Sunshine (2006)",             "Comedy|Drama"),
    (324, "The Kings of Summer (2013)",              "Adventure|Comedy|Drama"),
    (325, "Mid90s (2018)",                           "Drama"),

    # ── DISASTER ──────────────────────────────────────────────────────────────
    (326, "The Day After Tomorrow (2004)",           "Action|Adventure|Sci-Fi|Thriller"),
    (327, "San Andreas (2015)",                      "Action|Drama|Thriller"),
    (328, "2012 (2009)",                             "Action|Adventure|Sci-Fi|Thriller"),
    (329, "Twister (1996)",                          "Action|Adventure|Thriller"),
    (330, "Armageddon (1998)",                       "Action|Adventure|Sci-Fi|Thriller"),
    (331, "Dante's Peak (1997)",                     "Action|Adventure|Thriller"),
    (332, "The Perfect Storm (2000)",                "Action|Adventure|Drama|Thriller"),
    (333, "Deep Impact (1998)",                      "Drama|Sci-Fi|Thriller"),
    (334, "Volcano (1997)",                          "Action|Thriller"),
    (335, "Geostorm (2017)",                         "Action|Sci-Fi|Thriller"),

    # ── VAMPIRE / SUPERNATURAL ────────────────────────────────────────────────
    (336, "Interview with the Vampire (1994)",       "Drama|Fantasy|Horror"),
    (337, "Bram Stoker's Dracula (1992)",            "Fantasy|Horror|Romance"),
    (338, "Nosferatu (1922)",                        "Fantasy|Horror"),
    (339, "Let the Right One In (2008)",             "Drama|Fantasy|Horror|Romance"),
    (340, "What We Do in the Shadows (2014)",        "Comedy|Fantasy|Horror"),
    (341, "Only Lovers Left Alive (2013)",           "Drama|Fantasy|Horror|Romance"),
    (342, "Twilight (2008)",                         "Drama|Fantasy|Romance"),
    (343, "New Moon (2009)",                         "Drama|Fantasy|Romance"),
    (344, "Underworld (2003)",                       "Action|Fantasy|Horror|Thriller"),
    (345, "Blade (1998)",                            "Action|Fantasy|Horror|Thriller"),

    # ── ESPIONAGE ─────────────────────────────────────────────────────────────
    (346, "Casino Royale (2006)",                    "Action|Adventure|Thriller"),
    (347, "Skyfall (2012)",                          "Action|Adventure|Thriller"),
    (348, "No Time to Die (2021)",                   "Action|Adventure|Thriller"),
    (349, "Tinker Tailor Soldier Spy (2011)",        "Drama|Mystery|Thriller"),
    (350, "The Spy Who Came in from the Cold (1965)","Drama|Mystery|Thriller"),

    # ── ZOMBIE / POST-APOCALYPTIC ─────────────────────────────────────────────
    (351, "28 Days Later (2002)",                    "Drama|Horror|Sci-Fi|Thriller"),
    (352, "World War Z (2013)",                      "Action|Drama|Horror|Sci-Fi|Thriller"),
    (353, "I Am Legend (2007)",                      "Drama|Horror|Sci-Fi|Thriller"),
    (354, "The Road (2009)",                         "Drama|Sci-Fi|Thriller"),
    (355, "Children of Men (2006)",                  "Action|Drama|Sci-Fi|Thriller"),
    (356, "Snowpiercer (2013)",                      "Action|Drama|Sci-Fi|Thriller"),
    (357, "A Quiet Place (2018)",                    "Drama|Horror|Sci-Fi|Thriller"),
    (358, "Bird Box (2018)",                         "Drama|Horror|Mystery|Sci-Fi|Thriller"),
    (359, "The Girl with All the Gifts (2016)",      "Drama|Fantasy|Horror|Sci-Fi|Thriller"),
    (360, "Train to Busan (2016)",                   "Action|Horror|Thriller"),

    # ── SPACE / EXPLORATION ───────────────────────────────────────────────────
    (361, "Apollo 13 (1995)",                        "Adventure|Drama|History"),
    (362, "The Right Stuff (1983)",                  "Adventure|Drama|History"),
    (363, "Hidden Figures (2016)",                   "Biography|Drama|History"),
    (364, "First Man (2018)",                        "Biography|Drama|History"),
    (365, "Ad Astra (2019)",                         "Adventure|Drama|Mystery|Sci-Fi|Thriller"),
    (366, "Life (2017)",                             "Horror|Mystery|Sci-Fi|Thriller"),
    (367, "Passengers (2016)",                       "Adventure|Drama|Romance|Sci-Fi|Thriller"),
    (368, "Gravity (2013)",                          "Drama|Sci-Fi|Thriller"),
    (369, "Europa Report (2013)",                    "Drama|Mystery|Sci-Fi|Thriller"),
    (370, "The Midnight Sky (2020)",                 "Drama|Sci-Fi|Thriller"),

    # ── ROAD MOVIES ───────────────────────────────────────────────────────────
    (371, "Easy Rider (1969)",                       "Adventure|Drama"),
    (372, "Thelma & Louise (1991)",                  "Adventure|Crime|Drama"),
    (373, "Little Miss Sunshine (2006)",             "Adventure|Comedy|Drama"),
    (374, "Planes, Trains and Automobiles (1987)",   "Comedy|Drama"),
    (375, "Wild (2014)",                             "Adventure|Biography|Drama"),
    (376, "O Brother, Where Art Thou? (2000)",       "Adventure|Comedy|Crime|Drama|Musical"),
    (377, "Midnight Cowboy (1969)",                  "Drama"),
    (378, "Rain Man (1988)",                         "Drama"),
    (379, "Lost in Translation (2003)",              "Comedy|Drama|Romance"),
    (380, "The Secret Life of Walter Mitty (2013)",  "Adventure|Comedy|Drama|Fantasy|Romance"),

    # ── MOCKUMENTARY / SATIRE ─────────────────────────────────────────────────
    (381, "This Is Spinal Tap (1984)",               "Comedy|Music"),
    (382, "Best in Show (2000)",                     "Comedy"),
    (383, "Borat (2006)",                            "Comedy"),
    (384, "Dr. Strangelove (1964)",                  "Comedy|Drama|War"),
    (385, "Network (1976)",                          "Drama|Thriller"),
    (386, "Wag the Dog (1997)",                      "Comedy|Drama"),
    (387, "American Beauty (1999)",                  "Drama"),
    (388, "Idiocracy (2006)",                        "Adventure|Comedy|Sci-Fi"),
    (389, "Don't Look Up (2021)",                    "Comedy|Drama|Sci-Fi"),
    (390, "The Truman Show (1998)",                  "Comedy|Drama|Sci-Fi"),

    # ── RECENT HITS (2020s) ───────────────────────────────────────────────────
    (391, "Everything Everywhere All at Once (2022)","Action|Adventure|Comedy|Drama|Fantasy|Sci-Fi"),
    (392, "The Batman (2022)",                       "Action|Crime|Drama|Mystery|Thriller"),
    (393, "Doctor Strange in the Multiverse of Madness (2022)", "Action|Adventure|Fantasy|Horror|Sci-Fi"),
    (394, "Nope (2022)",                             "Horror|Mystery|Sci-Fi|Western"),
    (395, "The Whale (2022)",                        "Drama"),
    (396, "Tár (2022)",                              "Drama|Music"),
    (397, "Babylon (2022)",                          "Comedy|Drama|History"),
    (398, "All Quiet on the Western Front (2022)",   "Drama|War"),
    (399, "Triangle of Sadness (2022)",              "Comedy|Drama|Thriller"),
    (400, "The Menu (2022)",                         "Comedy|Horror|Thriller"),

    # ── ANIME FILM ────────────────────────────────────────────────────────────
    (401, "Your Name (2016)",                        "Animation|Drama|Fantasy|Romance"),
    (402, "A Silent Voice (2016)",                   "Animation|Drama|Romance"),
    (403, "Weathering with You (2019)",              "Animation|Drama|Fantasy|Romance"),
    (404, "Nausicaä of the Valley of the Wind (1984)","Action|Adventure|Animation|Fantasy|Sci-Fi"),
    (405, "Castle in the Sky (1986)",                "Action|Adventure|Animation|Children|Fantasy|Sci-Fi"),
    (406, "Grave of the Fireflies (1988)",           "Animation|Drama|War"),
    (407, "Paprika (2006)",                          "Animation|Fantasy|Sci-Fi|Thriller"),
    (408, "The End of Evangelion (1997)",            "Action|Animation|Drama|Sci-Fi"),
    (409, "Wolf Children (2012)",                    "Animation|Drama|Fantasy"),
    (410, "The Girl Who Leapt Through Time (2006)",  "Animation|Drama|Romance|Sci-Fi"),

    # ── BOLLYWOOD / HINDI ─────────────────────────────────────────────────────
    (411, "Dilwale Dulhania Le Jayenge (1995)",      "Drama|Musical|Romance"),
    (412, "Lagaan (2001)",                           "Drama|Musical|Sport"),
    (413, "Dil Chahta Hai (2001)",                   "Comedy|Drama|Romance"),
    (414, "Mughal-E-Azam (1960)",                    "Drama|History|Musical|Romance"),
    (415, "Sholay (1975)",                           "Action|Adventure|Drama|Western"),
    (416, "3 Idiots (2009)",                         "Comedy|Drama"),
    (417, "Taare Zameen Par (2007)",                 "Drama|Family"),
    (418, "Rang De Basanti (2006)",                  "Drama|History"),
    (419, "PK (2014)",                               "Comedy|Drama|Romance|Sci-Fi"),
    (420, "Queen (2014)",                            "Adventure|Comedy|Drama|Romance"),

    # ── TAMIL / SOUTH INDIAN ──────────────────────────────────────────────────
    (421, "Baahubali: The Beginning (2015)",         "Action|Adventure|Drama|Fantasy"),
    (422, "Baahubali 2: The Conclusion (2017)",      "Action|Adventure|Drama|Fantasy"),
    (423, "Enthiran (2010)",                         "Action|Drama|Romance|Sci-Fi|Thriller"),
    (424, "Vikram (2022)",                           "Action|Crime|Thriller"),
    (425, "KGF: Chapter 1 (2018)",                   "Action|Crime|Drama|Thriller"),
    (426, "KGF: Chapter 2 (2022)",                   "Action|Crime|Drama|Thriller"),
    (427, "Master (2021)",                           "Action|Crime|Drama|Thriller"),
    (428, "Beast (2022)",                            "Action|Thriller"),
    (429, "Roja (1992)",                             "Drama|Musical|Romance|Thriller"),
    (430, "Minnale (2001)",                          "Drama|Romance|Thriller"),

    # ── ADDITIONAL POPULAR ────────────────────────────────────────────────────
    (431, "The Wolf of Wall Street (2013)",          "Biography|Comedy|Crime|Drama"),
    (432, "Django Unchained (2012)",                 "Drama|Western"),
    (433, "Inglourious Basterds (2009)",             "Adventure|Drama|War"),
    (434, "Kill Bill: Vol. 1 (2003)",                "Action|Crime|Thriller"),
    (435, "Kill Bill: Vol. 2 (2004)",                "Action|Crime|Drama|Thriller"),
    (436, "Reservoir Dogs (1992)",                   "Crime|Drama|Mystery|Thriller"),
    (437, "Jackie Brown (1997)",                     "Crime|Drama|Thriller"),
    (438, "Hateful Eight (2015)",                    "Crime|Drama|Mystery|Western"),
    (439, "Once Upon a Time in Hollywood (2019)",    "Comedy|Drama"),
    (440, "Grindhouse: Planet Terror (2007)",        "Action|Horror|Sci-Fi|Thriller"),

    (441, "Vertigo (1958)",                          "Crime|Mystery|Romance|Thriller"),
    (442, "North by Northwest (1959)",               "Action|Adventure|Mystery|Thriller"),
    (443, "Rope (1948)",                             "Crime|Drama|Mystery|Thriller"),
    (444, "The Birds (1963)",                        "Drama|Horror|Mystery|Thriller"),
    (445, "Rebecca (1940)",                          "Drama|Film-Noir|Mystery|Romance|Thriller"),
    (446, "Dial M for Murder (1954)",                "Crime|Mystery|Thriller"),
    (447, "Witness for the Prosecution (1957)",      "Crime|Drama|Mystery"),
    (448, "Strangers on a Train (1951)",             "Crime|Mystery|Thriller"),
    (449, "Shadow of a Doubt (1943)",                "Crime|Drama|Film-Noir|Mystery|Thriller"),
    (450, "Notorious (1946)",                        "Drama|Film-Noir|Romance|Thriller"),

    (451, "Her (2013)",                              "Drama|Romance|Sci-Fi"),
    (452, "Lost in Translation (2003)",              "Comedy|Drama|Romance"),
    (453, "Eternal Sunshine of the Spotless Mind (2004)", "Drama|Romance|Sci-Fi"),
    (454, "Before Sunset (2004)",                    "Drama|Romance"),
    (455, "Before Midnight (2013)",                  "Drama|Romance"),
    (456, "Ruby Sparks (2012)",                      "Comedy|Drama|Fantasy|Romance"),
    (457, "Warm Bodies (2013)",                      "Comedy|Horror|Romance|Sci-Fi"),
    (458, "Crazy Stupid Love (2011)",                "Comedy|Drama|Romance"),
    (459, "The Holiday (2006)",                      "Comedy|Drama|Romance"),
    (460, "Love Actually (2003)",                    "Comedy|Drama|Romance"),

    (461, "Pan's Labyrinth (2006)",                  "Drama|Fantasy|War"),
    (462, "The Shape of Water (2017)",               "Adventure|Drama|Fantasy|Romance"),
    (463, "Crimson Peak (2015)",                     "Drama|Fantasy|Horror|Mystery|Romance|Thriller"),
    (464, "Beetlejuice (1988)",                      "Comedy|Fantasy|Horror"),
    (465, "Big Eyes (2014)",                         "Biography|Crime|Drama"),
    (466, "Ed Wood (1994)",                          "Biography|Comedy|Drama"),
    (467, "Batman Returns (1992)",                   "Action|Adventure|Fantasy"),
    (468, "Sleepy Hollow (1999)",                    "Fantasy|Horror|Mystery|Thriller"),
    (469, "Big Fish (2003)",                         "Drama|Fantasy|Romance"),
    (470, "Charlie and the Chocolate Factory (2005)","Adventure|Children|Comedy|Fantasy|Musical"),

    (471, "Dumb and Dumber (1994)",                  "Adventure|Comedy"),
    (472, "Ace Ventura: Pet Detective (1994)",       "Comedy|Crime"),
    (473, "The Mask (1994)",                         "Action|Comedy|Crime|Fantasy"),
    (474, "Liar Liar (1997)",                        "Comedy|Fantasy"),
    (475, "The Truman Show (1998)",                  "Comedy|Drama|Sci-Fi"),
    (476, "Bruce Almighty (2003)",                   "Comedy|Drama|Fantasy"),
    (477, "Eternal Sunshine of the Spotless Mind (2004)", "Drama|Romance|Sci-Fi"),
    (478, "Yes Man (2008)",                          "Comedy|Drama|Romance"),
    (479, "The Number 23 (2007)",                    "Crime|Mystery|Thriller"),
    (480, "Kick-Ass (2010)",                         "Action|Comedy|Crime"),

    (481, "The Prestige (2006)",                     "Drama|Mystery|Sci-Fi|Thriller"),
    (482, "Interstellar (2014)",                     "Adventure|Drama|Sci-Fi"),
    (483, "Tenet (2020)",                            "Action|Mystery|Sci-Fi|Thriller"),
    (484, "Memento (2000)",                          "Mystery|Thriller"),
    (485, "Following (1998)",                        "Crime|Drama|Mystery|Thriller"),
    (486, "Batman Begins (2005)",                    "Action|Crime|Drama|Thriller"),
    (487, "The Dark Knight (2008)",                  "Action|Crime|Drama|Thriller"),
    (488, "The Dark Knight Rises (2012)",            "Action|Crime|Drama|Thriller"),
    (489, "Inception (2010)",                        "Action|Adventure|Sci-Fi|Thriller"),
    (490, "Dunkirk (2017)",                          "Action|Drama|History|Thriller|War"),

    (491, "The Matrix Reloaded (2003)",              "Action|Sci-Fi|Thriller"),
    (492, "The Matrix Revolutions (2003)",           "Action|Sci-Fi|Thriller"),
    (493, "Speed Racer (2008)",                      "Action|Children|Comedy|Drama|Family|Sport"),
    (494, "Jupiter Ascending (2015)",                "Action|Adventure|Fantasy|Romance|Sci-Fi"),
    (495, "Cloud Atlas (2012)",                      "Action|Drama|Mystery|Sci-Fi|Thriller"),
    (496, "V for Vendetta (2005)",                   "Action|Drama|Sci-Fi|Thriller"),
    (497, "Watchmen (2009)",                         "Action|Drama|Mystery|Sci-Fi|Thriller"),
    (498, "The Fountain (2006)",                     "Drama|Mystery|Romance|Sci-Fi"),
    (499, "Requiem for a Dream (2000)",              "Drama"),
    (500, "Pi (1998)",                               "Drama|Mystery|Sci-Fi|Thriller"),
]

# Remove duplicates (some movies appear twice with different IDs — intended for variety)
seen_titles = set()
unique_movies = []
for m in MOVIES:
    key = m[1].lower()
    if key not in seen_titles:
        seen_titles.add(key)
        unique_movies.append(m)

movies_df = pd.DataFrame(unique_movies, columns=['movieId', 'title', 'genres'])
# Re-assign sequential IDs
movies_df['movieId'] = range(1, len(movies_df) + 1)

print(f"Total unique movies: {len(movies_df)}")
print(movies_df.head())

# Save movies.csv
movies_df.to_csv(os.path.join(DATA_DIR, 'movies.csv'), index=False)
print(f"✅ Saved movies.csv: {len(movies_df)} movies")

# =============================================================================
# GENERATE REALISTIC RATINGS
# =============================================================================
# Strategy:
#   - 610 users (matches MovieLens small)
#   - Each user rates 20-200 movies (realistic range)
#   - Popular movies get more ratings (power-law distribution)
#   - Ratings follow a slightly positive-skewed distribution (people rate
#     movies they like more than ones they hated)
#   - Genre affinity: each user secretly prefers certain genres
# =============================================================================

NUM_USERS  = 610
NUM_MOVIES = len(movies_df)
all_movie_ids = movies_df['movieId'].values

# Build genre list per movie for affinity scoring
movie_genre_map = dict(zip(movies_df['movieId'], movies_df['genres']))

# All unique genres
ALL_GENRES = list(set(
    g for gs in movies_df['genres'] for g in gs.split('|')
))

# Give each user genre affinities (random weights per genre)
user_genre_affinity = {}
for uid in range(1, NUM_USERS + 1):
    # Each user strongly likes 2-4 genres, mildly likes others
    liked_genres = np.random.choice(ALL_GENRES, size=np.random.randint(2, 5), replace=False)
    affinity = {}
    for g in ALL_GENRES:
        affinity[g] = 0.8 if g in liked_genres else 0.2
    user_genre_affinity[uid] = affinity

# Popularity weight: some movies are universally more popular
# Using a power law — a few movies get many ratings
movie_popularity = np.random.power(0.4, NUM_MOVIES)
movie_popularity = movie_popularity / movie_popularity.sum()

print(f"\n[INFO] Generating ratings for {NUM_USERS} users...")

records = []
base_timestamp = 1000000000

for uid in range(1, NUM_USERS + 1):
    # How many movies this user rates (between 20 and 200)
    n_ratings = np.random.randint(20, 200)

    # Sample movies based on popularity (popular movies rated more)
    rated_movies = np.random.choice(
        all_movie_ids,
        size=min(n_ratings, NUM_MOVIES),
        replace=False,
        p=movie_popularity
    )

    # User's personal rating bias (some are generous, some are harsh)
    user_bias = np.random.uniform(-0.5, 0.8)

    for mid in rated_movies:
        # Base rating depends on genre affinity
        genres = movie_genre_map.get(mid, '').split('|')
        genre_score = np.mean([user_genre_affinity[uid].get(g, 0.3) for g in genres])

        # Convert affinity score to a rating
        # Affinity 0.0 → rating ~1.5, Affinity 1.0 → rating ~5.0
        base_rating = 1.5 + genre_score * 3.5 + user_bias

        # Add some noise
        rating = base_rating + np.random.normal(0, 0.7)

        # Round to nearest 0.5, clamp to [0.5, 5.0]
        rating = round(rating * 2) / 2
        rating = max(0.5, min(5.0, rating))

        timestamp = base_timestamp + np.random.randint(0, 500000000)
        records.append((uid, int(mid), float(rating), int(timestamp)))

ratings_df = pd.DataFrame(records, columns=['userId', 'movieId', 'rating', 'timestamp'])
# Remove any duplicates
ratings_df = ratings_df.drop_duplicates(subset=['userId', 'movieId'])

print(f"Total ratings: {len(ratings_df)}")
print(f"Rating distribution:\n{ratings_df['rating'].value_counts().sort_index()}")
print(f"Avg rating: {ratings_df['rating'].mean():.2f}")

ratings_df.to_csv(os.path.join(DATA_DIR, 'ratings.csv'), index=False)
print(f"✅ Saved ratings.csv: {len(ratings_df)} ratings")

print(f"\n{'='*50}")
print(f"  Dataset Summary")
print(f"{'='*50}")
print(f"  Movies  : {len(movies_df)}")
print(f"  Users   : {ratings_df['userId'].nunique()}")
print(f"  Ratings : {len(ratings_df)}")
print(f"  Avg rating: {ratings_df['rating'].mean():.2f}")
print(f"  Sparsity: {(1 - len(ratings_df)/(ratings_df['userId'].nunique()*len(movies_df)))*100:.1f}%")
print(f"\n  Run train_all.py to train ML models on this data.")