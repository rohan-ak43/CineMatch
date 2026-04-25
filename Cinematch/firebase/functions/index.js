// =============================================================================
// CineMatch — Firebase Cloud Functions (index.js)
// =============================================================================
// This file replaces the MySQL database AND most Flask auth routes.
//
// All functions are HTTP-triggered and exposed as:
//   https://us-central1-YOUR_PROJECT.cloudfunctions.net/api/...
//
// OR via Firebase Hosting rewrites at:
//   https://YOUR_PROJECT.web.app/api/...
//
// Collections in Firestore:
//   users/{uid}                        — user profiles
//   movies/{movieId}                   — movie catalogue
//   ratings/{uid_movieId}              — user ratings
//   reviews/{reviewId}                 — user reviews + ML sentiment
//   watch_history/{uid}/items/{movieId}— per-user watch history
//   recommendations_log/{logId}        — recommendation sessions
// =============================================================================

const functions  = require("firebase-functions");
const admin      = require("firebase-admin");
const express    = require("express");
const cors       = require("cors");
const axios      = require("axios");

// ── INITIALISE FIREBASE ADMIN ─────────────────────────────────────────────────
// Admin SDK bypasses Firestore security rules — safe to use server-side only.
admin.initializeApp();

const db   = admin.firestore();
const auth = admin.auth();

// ── EXPRESS APP ───────────────────────────────────────────────────────────────
const app = express();
app.use(cors({ origin: true }));          // Allow all origins (restrict in production)
app.use(express.json());

// Flask ML server URL — update this when you deploy Flask
// For local dev: "http://127.0.0.1:5000"
// For production: your deployed Flask URL (e.g. Railway, Render, etc.)
const FLASK_URL = process.env.FLASK_URL || "http://127.0.0.1:5000";

// =============================================================================
// MIDDLEWARE — Verify Firebase ID Token
// =============================================================================
// Firebase Auth gives users an ID token after login.
// We verify it here before allowing access to protected routes.
// =============================================================================

async function verifyToken(req, res, next) {
  const authHeader = req.headers.authorization || "";

  // Token format: "Bearer <idToken>"
  if (!authHeader.startsWith("Bearer ")) {
    return res.status(401).json({ error: "Missing or invalid Authorization header" });
  }

  const idToken = authHeader.split("Bearer ")[1];

  try {
    // Verify the token with Firebase Auth
    const decodedToken = await auth.verifyIdToken(idToken);
    req.user = decodedToken;  // Attach decoded user (uid, email, etc.) to request
    next();
  } catch (err) {
    return res.status(401).json({ error: "Invalid or expired token" });
  }
}

// =============================================================================
// HELPER — Call Flask ML Server
// =============================================================================
// The Flask server handles all heavy ML inference.
// We call it from Cloud Functions and return results to the frontend.
// =============================================================================

async function callFlask(endpoint, method = "GET", body = null, token = null) {
  try {
    const config = {
      method,
      url: `${FLASK_URL}${endpoint}`,
      headers: {
        "Content-Type": "application/json",
        // Pass a special internal key so Flask knows the call is from Cloud Functions
        "X-Internal-Key": process.env.INTERNAL_KEY || "cinematch-internal-2024",
      },
      ...(body ? { data: body } : {}),
      timeout: 30000,  // 30 second timeout
    };

    const response = await axios(config);
    return { ok: true, data: response.data };
  } catch (err) {
    const errMsg = err.response?.data?.error || err.message || "Flask server unreachable";
    return { ok: false, error: errMsg };
  }
}

// =============================================================================
// HELPER — Seed movies into Firestore (run once)
// =============================================================================

async function seedMoviesIfEmpty() {
  const snapshot = await db.collection("movies").limit(1).get();
  if (!snapshot.empty) return; // Already seeded

  const movies = [
    { movieId: 1,  title: "Toy Story (1995)",                    genres: "Adventure|Animation|Children|Comedy|Fantasy", language: "English", year: 1995 },
    { movieId: 2,  title: "Jumanji (1995)",                      genres: "Adventure|Children|Fantasy",                  language: "English", year: 1995 },
    { movieId: 3,  title: "Grumpier Old Men (1995)",             genres: "Comedy|Romance",                              language: "English", year: 1995 },
    { movieId: 4,  title: "Waiting to Exhale (1995)",            genres: "Comedy|Drama|Romance",                        language: "English", year: 1995 },
    { movieId: 5,  title: "Father of the Bride Part II (1995)",  genres: "Comedy",                                      language: "English", year: 1995 },
    { movieId: 6,  title: "Heat (1995)",                         genres: "Action|Crime|Thriller",                       language: "English", year: 1995 },
    { movieId: 7,  title: "Sabrina (1995)",                      genres: "Comedy|Romance",                              language: "English", year: 1995 },
    { movieId: 8,  title: "Tom and Huck (1995)",                 genres: "Adventure|Children",                          language: "English", year: 1995 },
    { movieId: 9,  title: "Sudden Death (1995)",                 genres: "Action",                                      language: "English", year: 1995 },
    { movieId: 10, title: "GoldenEye (1995)",                    genres: "Action|Adventure|Thriller",                   language: "English", year: 1995 },
    { movieId: 11, title: "American President, The (1995)",      genres: "Comedy|Drama|Romance",                        language: "English", year: 1995 },
    { movieId: 12, title: "Dracula: Dead and Loving It (1995)",  genres: "Comedy|Horror",                               language: "English", year: 1995 },
    { movieId: 13, title: "Balto (1995)",                        genres: "Adventure|Animation|Children",                language: "English", year: 1995 },
    { movieId: 14, title: "Nixon (1995)",                        genres: "Drama",                                       language: "English", year: 1995 },
    { movieId: 15, title: "Cutthroat Island (1995)",             genres: "Action|Adventure|Romance",                    language: "English", year: 1995 },
    { movieId: 16, title: "Casino (1995)",                       genres: "Crime|Drama",                                 language: "English", year: 1995 },
    { movieId: 17, title: "Sense and Sensibility (1995)",        genres: "Drama|Romance",                               language: "English", year: 1995 },
    { movieId: 18, title: "Four Rooms (1995)",                   genres: "Comedy|Mystery",                              language: "English", year: 1995 },
    { movieId: 19, title: "Ace Ventura: When Nature Calls (1995)",genres: "Comedy",                                     language: "English", year: 1995 },
    { movieId: 20, title: "Money Train (1995)",                  genres: "Action|Comedy|Crime|Drama|Thriller",          language: "English", year: 1995 },
    { movieId: 21, title: "Get Shorty (1995)",                   genres: "Comedy|Crime|Thriller",                       language: "English", year: 1995 },
    { movieId: 22, title: "Copycat (1995)",                      genres: "Crime|Drama|Thriller",                        language: "English", year: 1995 },
    { movieId: 23, title: "Assassins (1995)",                    genres: "Action|Thriller",                             language: "English", year: 1995 },
    { movieId: 24, title: "Powder (1995)",                       genres: "Drama|Sci-Fi",                                language: "English", year: 1995 },
    { movieId: 25, title: "Leaving Las Vegas (1995)",            genres: "Drama|Romance",                               language: "English", year: 1995 },
    { movieId: 26, title: "Othello (1995)",                      genres: "Drama|Romance",                               language: "English", year: 1995 },
    { movieId: 27, title: "Now and Then (1995)",                 genres: "Children|Comedy|Drama",                       language: "English", year: 1995 },
    { movieId: 28, title: "Persuasion (1995)",                   genres: "Drama|Romance",                               language: "English", year: 1995 },
    { movieId: 29, title: "City of Lost Children (1995)",        genres: "Adventure|Drama|Fantasy|Mystery|Sci-Fi",      language: "French",  year: 1995 },
    { movieId: 30, title: "Shanghai Triad (1995)",               genres: "Crime|Drama",                                 language: "Chinese", year: 1995 },
  ];

  const batch = db.batch();
  movies.forEach(movie => {
    const ref = db.collection("movies").doc(String(movie.movieId));
    batch.set(ref, {
      ...movie,
      avgRating:   0,
      ratingCount: 0,
      createdAt:   admin.firestore.FieldValue.serverTimestamp(),
    });
  });

  await batch.commit();
  console.log("✅ Seeded 30 movies into Firestore");
}

// =============================================================================
// ROUTE: GET /api/health
// =============================================================================

app.get("/api/health", async (req, res) => {
  // Check Flask ML server connectivity
  const flaskCheck = await callFlask("/api/health");
  res.json({
    status:       "ok",
    firebase:     "connected",
    flaskMl:      flaskCheck.ok ? "connected" : "offline",
    timestamp:    new Date().toISOString(),
    version:      "2.0.0-firebase",
  });
});

// =============================================================================
// ROUTE: POST /api/auth/sync-user
// =============================================================================
// Called right after Firebase login/register on the frontend.
// Creates or updates the user's Firestore profile document.
// Firebase Auth handles the actual password — we just store extra profile info.
// =============================================================================

app.post("/api/auth/sync-user", verifyToken, async (req, res) => {
  const { uid, email, name: authName } = req.user;
  const { name } = req.body;

  const displayName = name || authName || email.split("@")[0];

  try {
    const userRef = db.collection("users").doc(uid);
    const snap    = await userRef.get();

    if (!snap.exists) {
      // First time — create profile
      await userRef.set({
        name:       displayName,
        email:      email,
        createdAt:  admin.firestore.FieldValue.serverTimestamp(),
        lastLogin:  admin.firestore.FieldValue.serverTimestamp(),
        isActive:   true,
      });

      // Also update Firebase Auth display name
      await auth.updateUser(uid, { displayName });

      return res.status(201).json({
        message: "Profile created",
        user: { id: uid, name: displayName, email },
      });
    } else {
      // Returning user — update last login
      await userRef.update({ lastLogin: admin.firestore.FieldValue.serverTimestamp() });
      const data = snap.data();
      return res.json({
        message: "Login recorded",
        user: { id: uid, name: data.name, email: data.email },
      });
    }
  } catch (err) {
    console.error("sync-user error:", err);
    return res.status(500).json({ error: err.message });
  }
});

// =============================================================================
// ROUTE: POST /api/recommend
// =============================================================================
// Calls Flask ML server for recommendations, logs session to Firestore.
// =============================================================================

app.post("/api/recommend", verifyToken, async (req, res) => {
  const uid = req.user.uid;
  const { mood_text, genre, language, liked_movie, top_n = 10 } = req.body;

  // Forward request to Flask ML server
  const result = await callFlask("/api/recommend", "POST", {
    mood_text,
    genre,
    language,
    liked_movie,
    top_n,
    user_id: uid,
  });

  if (!result.ok) {
    return res.status(503).json({ error: "ML server unavailable: " + result.error });
  }

  // Log recommendation session to Firestore (async, don't await)
  db.collection("recommendations_log").add({
    userId:         uid,
    moodInput:      mood_text    || null,
    detectedMood:   result.data.detected_mood || null,
    genreFilter:    genre        || null,
    languageFilter: language     || null,
    moviesReturned: (result.data.recommendations || []).map(m => m.id),
    algorithmUsed:  result.data.algorithm || "hybrid",
    createdAt:      admin.firestore.FieldValue.serverTimestamp(),
  }).catch(console.error);

  res.json(result.data);
});

// =============================================================================
// ROUTE: POST /api/predict_rating
// =============================================================================

app.post("/api/predict_rating", verifyToken, async (req, res) => {
  const uid = req.user.uid;
  const { movie_id } = req.body;

  if (!movie_id) return res.status(400).json({ error: "movie_id is required" });

  const result = await callFlask("/api/predict_rating", "POST", {
    movie_id,
    user_id: uid,
  });

  if (!result.ok) return res.status(503).json({ error: result.error });
  res.json(result.data);
});

// =============================================================================
// ROUTE: POST /api/analyze_review
// =============================================================================

app.post("/api/analyze_review", verifyToken, async (req, res) => {
  const { review_text } = req.body;
  if (!review_text) return res.status(400).json({ error: "review_text is required" });

  const result = await callFlask("/api/analyze_review", "POST", { review_text });
  if (!result.ok) return res.status(503).json({ error: result.error });
  res.json(result.data);
});

// =============================================================================
// ROUTE: POST /api/detect_mood
// =============================================================================

app.post("/api/detect_mood", async (req, res) => {
  const { text } = req.body;
  if (!text) return res.status(400).json({ error: "text is required" });

  const result = await callFlask("/api/detect_mood", "POST", { text });
  if (!result.ok) return res.status(503).json({ error: result.error });
  res.json(result.data);
});

// =============================================================================
// ROUTE: POST /api/rate_movie
// =============================================================================
// Saves rating to Firestore, then recomputes movie's average rating.
// =============================================================================

app.post("/api/rate_movie", verifyToken, async (req, res) => {
  const uid = req.user.uid;
  const { movie_id, rating } = req.body;

  if (!movie_id || rating == null) {
    return res.status(400).json({ error: "movie_id and rating are required" });
  }
  if (rating < 0.5 || rating > 5.0) {
    return res.status(400).json({ error: "Rating must be between 0.5 and 5.0" });
  }

  const ratingId  = `${uid}_${movie_id}`;
  const ratingRef = db.collection("ratings").doc(ratingId);
  const movieRef  = db.collection("movies").doc(String(movie_id));

  try {
    // Save / overwrite rating
    await ratingRef.set({
      userId:    uid,
      movieId:   movie_id,
      rating:    parseFloat(rating),
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
      updatedAt: admin.firestore.FieldValue.serverTimestamp(),
    }, { merge: true });

    // Also add to watch history
    await db.collection("watch_history")
      .doc(uid)
      .collection("items")
      .doc(String(movie_id))
      .set({
        movieId:   movie_id,
        watchedAt: admin.firestore.FieldValue.serverTimestamp(),
      }, { merge: true });

    // Recompute movie average rating using a Firestore transaction
    await db.runTransaction(async (transaction) => {
      // Get all ratings for this movie
      const ratingsSnap = await db.collection("ratings")
        .where("movieId", "==", movie_id)
        .get();

      const total  = ratingsSnap.size;
      const sumVal = ratingsSnap.docs.reduce((sum, d) => sum + d.data().rating, 0);
      const avg    = total > 0 ? sumVal / total : 0;

      transaction.update(movieRef, {
        avgRating:   parseFloat(avg.toFixed(2)),
        ratingCount: total,
      });
    });

    res.json({ message: "Rating saved!", rating: parseFloat(rating) });
  } catch (err) {
    console.error("rate_movie error:", err);
    res.status(500).json({ error: err.message });
  }
});

// =============================================================================
// ROUTE: POST /api/submit_review
// =============================================================================
// Runs ML sentiment analysis, saves review + sentiment to Firestore.
// =============================================================================

app.post("/api/submit_review", verifyToken, async (req, res) => {
  const uid = req.user.uid;
  const { movie_id, review_text } = req.body;

  if (!movie_id || !review_text) {
    return res.status(400).json({ error: "movie_id and review_text are required" });
  }
  if (review_text.length < 10) {
    return res.status(400).json({ error: "Review too short (min 10 characters)" });
  }

  // Run ML sentiment analysis via Flask
  let sentiment   = "neutral";
  let confidence  = 0;

  const mlResult = await callFlask("/api/analyze_review", "POST", { review_text });
  if (mlResult.ok) {
    sentiment  = mlResult.data.sentiment  || "neutral";
    confidence = mlResult.data.confidence || 0;
  }

  try {
    const reviewRef = await db.collection("reviews").add({
      userId:     uid,
      movieId:    movie_id,
      reviewText: review_text,
      sentiment,
      confidence: parseFloat(confidence.toFixed(1)),
      createdAt:  admin.firestore.FieldValue.serverTimestamp(),
    });

    res.status(201).json({
      message:   "Review submitted!",
      reviewId:  reviewRef.id,
      sentiment,
      confidence: parseFloat(confidence.toFixed(1)),
    });
  } catch (err) {
    console.error("submit_review error:", err);
    res.status(500).json({ error: err.message });
  }
});

// =============================================================================
// ROUTE: GET /api/get_history
// =============================================================================
// Returns a user's watch history, enriched with movie + rating + review data.
// =============================================================================

app.get("/api/get_history", verifyToken, async (req, res) => {
  const uid   = req.user.uid;
  const limit = Math.min(parseInt(req.query.limit) || 20, 50);

  try {
    // Get watch history items (subcollection)
    const histSnap = await db.collection("watch_history")
      .doc(uid)
      .collection("items")
      .orderBy("watchedAt", "desc")
      .limit(limit)
      .get();

    if (histSnap.empty) return res.json({ history: [], total: 0 });

    const movieIds = histSnap.docs.map(d => d.data().movieId);

    // Batch-fetch movies
    const movieDocs = await Promise.all(
      movieIds.map(id => db.collection("movies").doc(String(id)).get())
    );

    // Batch-fetch ratings for this user
    const ratingDocs = await Promise.all(
      movieIds.map(id =>
        db.collection("ratings").doc(`${uid}_${id}`).get()
      )
    );

    // Batch-fetch reviews for this user + these movies
    const reviewsSnap = await db.collection("reviews")
      .where("userId", "==", uid)
      .where("movieId", "in", movieIds.slice(0, 10)) // Firestore "in" limit = 10
      .get();

    // Build a lookup map: movieId → review
    const reviewMap = {};
    reviewsSnap.docs.forEach(d => {
      reviewMap[d.data().movieId] = d.data();
    });

    // Assemble response
    const history = histSnap.docs.map((histDoc, i) => {
      const histData   = histDoc.data();
      const movieData  = movieDocs[i].exists  ? movieDocs[i].data()  : {};
      const ratingData = ratingDocs[i].exists ? ratingDocs[i].data() : {};
      const reviewData = reviewMap[histData.movieId] || {};

      return {
        movie_id:   histData.movieId,
        title:      movieData.title    || `Movie #${histData.movieId}`,
        genre:      movieData.genres   || "",
        language:   movieData.language || "English",
        watched_at: histData.watchedAt?.toDate().toISOString() || null,
        rating:     ratingData.rating  || null,
        sentiment:  reviewData.sentiment || null,
      };
    });

    res.json({ history, total: history.length });
  } catch (err) {
    console.error("get_history error:", err);
    res.status(500).json({ error: err.message });
  }
});

// =============================================================================
// ROUTE: GET /api/movies
// =============================================================================

app.get("/api/movies", verifyToken, async (req, res) => {
  const { genre, language, limit: lim = 30 } = req.query;
  const limit = Math.min(parseInt(lim), 100);

  try {
    // Seed on first call if collection is empty
    await seedMoviesIfEmpty();

    let query = db.collection("movies").limit(limit);
    if (language) query = query.where("language", "==", language);

    const snap = await query.get();
    let movies = snap.docs.map(d => ({ id: d.id, ...d.data() }));

    // Client-side genre filter (Firestore doesn't support LIKE)
    if (genre) {
      movies = movies.filter(m =>
        (m.genres || "").toLowerCase().includes(genre.toLowerCase())
      );
    }

    res.json({ movies, total: movies.length });
  } catch (err) {
    console.error("movies error:", err);
    res.status(500).json({ error: err.message });
  }
});

// =============================================================================
// ROUTE: GET /api/stats
// =============================================================================

app.get("/api/stats", verifyToken, async (req, res) => {
  try {
    const [moviesSnap, ratingsSnap, usersSnap] = await Promise.all([
      db.collection("movies").count().get(),
      db.collection("ratings").count().get(),
      db.collection("users").count().get(),
    ]);

    // Average rating across all ratings
    const ratingSample = await db.collection("ratings").limit(200).get();
    const ratings      = ratingSample.docs.map(d => d.data().rating);
    const avgRating    = ratings.length
      ? (ratings.reduce((a, b) => a + b, 0) / ratings.length).toFixed(2)
      : 0;

    res.json({
      total_movies:  moviesSnap.data().count,
      total_ratings: ratingsSnap.data().count,
      total_users:   usersSnap.data().count,
      avg_rating:    parseFloat(avgRating),
    });
  } catch (err) {
    console.error("stats error:", err);
    res.status(500).json({ error: err.message });
  }
});

// =============================================================================
// ROUTE: POST /api/seed-movies   (admin utility — protect in production)
// =============================================================================

app.post("/api/seed-movies", async (req, res) => {
  await seedMoviesIfEmpty();
  res.json({ message: "Seed complete (or already seeded)" });
});

// =============================================================================
// EXPORT — Expose Express app as a single Cloud Function named "api"
// =============================================================================
// All routes above are accessible at:
//   https://YOUR_REGION-YOUR_PROJECT.cloudfunctions.net/api/...
// =============================================================================

exports.api = functions
  .runWith({
    timeoutSeconds: 60,
    memory: "512MB",
  })
  .https.onRequest(app);