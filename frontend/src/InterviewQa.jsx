import { useState } from "react";

export default function InterviewQAGenerator() {
  const [file, setFile] = useState(null);
  const [jd, setJd] = useState("");
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [dashboardData, setDashboardData] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1); // 1: Upload, 2: Questions, 3: Dashboard

  const handleUpload = (e) => setFile(e.target.files[0]);
  const handleJdChange = (e) => setJd(e.target.value);

  const handleGenerate = async () => {
    if (!file || !jd.trim()) {
      alert("Please upload a resume and provide job description");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("resume", file);
    formData.append("job_description", jd);
    formData.append("candidate_response", "");

    try {
      const res = await fetch("http://127.0.0.1:8000/run-interview-evaluation/", {
        method: "POST",
        body: formData,
      });
      
      const data = await res.json();
      
      if (data.success) {
        setQuestions(data.data || []);
        setSessionId(data.session_id);
        setStep(2);
        setDashboardData(null);
      } else {
        alert(data.message || "Error generating questions");
      }
    } catch (err) {
      console.error("Error:", err);
      alert("Error generating questions. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (idx, value) => {
    setAnswers((prev) => ({ ...prev, [idx]: value }));
  };

  const handleSubmitAnswers = async () => {
    if(answers.length !== questions.length) {
      alert("Please answer all questions before submitting.");
      return;
    }
    if (!sessionId) {
      alert("Session expired. Please generate questions again.");
      return;
    }

    const hasAnswers = Object.values(answers).some(answer => answer.trim());
    if (!hasAnswers) {
      alert("Please provide at least one answer before submitting.");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("session_id", sessionId);

    const payload = questions.map((question, idx) => ({
      question,
      answer: answers[idx] || "",
    }));

    formData.append("answers", JSON.stringify(payload));

    try {
      const res = await fetch("http://127.0.0.1:8000/submit-mock-answers/", {
        method: "POST",
        body: formData,
      });
      
      const data = await res.json();
      
      if (data.success) {
        setDashboardData(data.data || {});
        setStep(3);
      } else {
        alert(data.message || "Error evaluating answers");
      }
    } catch (err) {
      console.error("Error:", err);
      alert("Error submitting answers. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleRestart = () => {
    setFile(null);
    setJd("");
    setQuestions([]);
    setAnswers({});
    setDashboardData(null);
    setSessionId(null);
    setStep(1);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreBg = (score) => {
    if (score >= 80) return "bg-green-100 border-green-300";
    if (score >= 60) return "bg-yellow-100 border-yellow-300";
    return "bg-red-100 border-red-300";
  };

  const getGradientBg = (score) => {
    if (score >= 80) return "bg-gradient-to-br from-green-400 to-emerald-500";
    if (score >= 60) return "bg-gradient-to-br from-yellow-400 to-orange-500";
    return "bg-gradient-to-br from-red-400 to-pink-500";
  };

  const ScoreCard = ({ title, score, icon, delay = 0 }) => (
    <div 
      className={`${getGradientBg(score)} rounded-2xl p-6 text-white shadow-xl transform hover:scale-105 transition-all duration-300`}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-3xl">{icon}</span>
        <span className="text-3xl font-bold">{score}</span>
      </div>
      <h3 className="text-lg font-semibold opacity-90">{title}</h3>
      <div className="mt-3 bg-white/20 rounded-full h-2">
        <div 
          className="bg-white rounded-full h-2 transition-all duration-1000 ease-out"
          style={{ width: `${score}%` }}
        ></div>
      </div>
    </div>
  );

  const FeedbackSection = ({ title, items, bgColor, icon, textColor = "text-gray-700" }) => (
    <div className={`${bgColor} rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow duration-300`}>
      <h3 className={`text-xl font-bold ${textColor} mb-4 flex items-center gap-2`}>
        <span className="text-2xl">{icon}</span>
        {title}
      </h3>
      {Array.isArray(items) ? (
        <ul className="space-y-2">
          {items.map((item, idx) => (
            <li key={idx} className={`flex items-start gap-2 ${textColor}`}>
              <span className="text-blue-500 mt-1">•</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className={textColor}>{items}</p>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 bg-clip-text text-transparent mb-2 animate-pulse">
            🎯 AI Interview Coach
          </h1>
          <p className="text-gray-600 text-lg">Master your behavioral interviews with AI-powered feedback</p>
        </div>

        {/* Progress Steps */}
        <div className="flex justify-center mb-8">
          <div className="flex items-center space-x-4">
            <div className={`flex items-center justify-center w-12 h-12 rounded-full text-lg font-bold transition-all duration-300 ${step >= 1 ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg' : 'bg-gray-300 text-gray-600'}`}>
              1
            </div>
            <div className={`w-20 h-2 rounded-full transition-all duration-300 ${step >= 2 ? 'bg-gradient-to-r from-purple-600 to-blue-600' : 'bg-gray-300'}`}></div>
            <div className={`flex items-center justify-center w-12 h-12 rounded-full text-lg font-bold transition-all duration-300 ${step >= 2 ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg' : 'bg-gray-300 text-gray-600'}`}>
              2
            </div>
            <div className={`w-20 h-2 rounded-full transition-all duration-300 ${step >= 3 ? 'bg-gradient-to-r from-purple-600 to-blue-600' : 'bg-gray-300'}`}></div>
            <div className={`flex items-center justify-center w-12 h-12 rounded-full text-lg font-bold transition-all duration-300 ${step >= 3 ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg' : 'bg-gray-300 text-gray-600'}`}>
              3
            </div>
          </div>
        </div>

        {/* Step 1: Upload and Generate */}
        {step === 1 && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-6 hover:shadow-2xl transition-shadow duration-300">
            <h2 className="text-3xl font-bold text-gray-800 mb-6 flex items-center gap-2">
              📄 Upload Your Details
            </h2>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Upload Resume (PDF or DOC):
                </label>
                <div className="relative">
                  <input 
                    type="file" 
                    onChange={handleUpload} 
                    accept=".pdf,.doc,.docx"
                    className="w-full p-4 border-2 border-dashed border-purple-300 rounded-xl hover:border-purple-400 focus:border-purple-500 focus:outline-none transition-colors"
                  />
                  {file && (
                    <div className="mt-3 text-sm text-green-600 flex items-center gap-2 bg-green-50 p-2 rounded-lg">
                      ✅ <span className="font-medium">{file.name}</span>
                    </div>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Job Description:
                </label>
                <textarea
                  className="w-full border-2 border-gray-300 rounded-xl p-4 focus:border-purple-500 focus:outline-none transition-colors resize-none"
                  rows={8}
                  value={jd}
                  onChange={handleJdChange}
                  placeholder="Paste the job description here..."
                />
              </div>
                  
              <button
                className={`w-full py-4 px-6 rounded-xl font-bold text-white text-lg transition-all duration-300 ${
                  loading 
                    ? 'bg-gray-400 cursor-not-allowed' 
                    : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 transform hover:scale-105 shadow-lg hover:shadow-xl'
                }`}
                onClick={handleGenerate}
                disabled={loading}
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></div>
                    Generating Questions...
                  </div>
                ) : (
                  "🚀 Generate Interview Questions"
                )}
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Answer Questions */}
        {step === 2 && questions.length > 0 && (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <h2 className="text-3xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                💭 Interview Questions
              </h2>
              
              <div className="space-y-6">
                {questions.map((q, idx) => (
                  <div key={idx} className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border-l-4 border-purple-500 hover:shadow-lg transition-shadow duration-300">
                    <p className="text-lg font-semibold text-gray-800 mb-4">
                      {idx + 1}. {q}
                    </p>
                    <textarea
                      className="w-full border-2 border-gray-300 rounded-xl p-4 focus:border-purple-500 focus:outline-none transition-colors resize-none"
                      rows={4}
                      value={answers[idx] || ""}
                      onChange={(e) => handleAnswerChange(idx, e.target.value)}
                      placeholder="Share your experience and insights here..."
                    />
                  </div>
                ))}

                <div className="flex space-x-4">
                  <button
                    className="flex-1 py-4 px-6 bg-gray-500 text-white rounded-xl font-bold hover:bg-gray-600 transition-colors"
                    onClick={handleRestart}
                  >
                    ← Start Over
                  </button>
                  <button
                    className={`flex-1 py-4 px-6 rounded-xl font-bold text-white transition-all duration-300 ${
                      loading 
                        ? 'bg-gray-400 cursor-not-allowed' 
                        : 'bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 transform hover:scale-105 shadow-lg'
                    }`}
                    onClick={handleSubmitAnswers}
                    disabled={loading}
                  >
                    {loading ? (
                      <div className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></div>
                        Analyzing...
                      </div>
                    ) : (
                      "📊 View Dashboard"
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Dashboard */}
        {step === 3 && dashboardData && (
          <div className="space-y-8 animate-fadeIn">
            {/* Main Header */}
            <div className="text-center bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-2xl p-8 shadow-2xl">
              <h2 className="text-4xl font-bold mb-2">🎯 Your Performance Dashboard</h2>
              <p className="text-xl opacity-90">Complete analysis of your interview readiness</p>
            </div>

            {/* Success Prediction */}
            {dashboardData.success_prediction && (
              <div className="bg-white rounded-2xl p-8 shadow-xl">
                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold text-gray-800 mb-4">🎯 Success Prediction</h3>
                  <div className={`inline-flex items-center justify-center w-32 h-32 rounded-full ${getGradientBg(dashboardData.success_prediction.score)} text-white shadow-2xl`}>
                    <span className="text-4xl font-bold">{dashboardData.success_prediction.score}%</span>
                  </div>
                  <p className="text-gray-600 mt-4 text-lg">{dashboardData.success_prediction.justification}</p>
                </div>
              </div>
            )}

            {/* Score Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Resume Analysis Scores */}
              {dashboardData.resume_analysis && (
                <>
                  <ScoreCard 
                    title="Resume Clarity" 
                    score={dashboardData.resume_analysis.clarity} 
                    icon="📝" 
                    delay={100}
                  />
                  <ScoreCard 
                    title="Relevance" 
                    score={dashboardData.resume_analysis.relevance} 
                    icon="🎯" 
                    delay={200}
                  />
                  <ScoreCard 
                    title="Structure" 
                    score={dashboardData.resume_analysis.structure} 
                    icon="🏗️" 
                    delay={300}
                  />
                  <ScoreCard 
                    title={`Experience (${dashboardData.resume_analysis.experience} years)`} 
                    score={Math.min(dashboardData.resume_analysis.experience * 20, 100)} 
                    icon="⭐" 
                    delay={400}
                  />
                </>
              )}

              {/* Mock Interview Scores */}
              {dashboardData.mock_response && (
                <>
                  <ScoreCard 
                    title="Interview Tone" 
                    score={dashboardData.mock_response.tone} 
                    icon="🗣️" 
                    delay={500}
                  />
                  <ScoreCard 
                    title="Confidence" 
                    score={dashboardData.mock_response.confidence} 
                    icon="💪" 
                    delay={600}
                  />
                  <ScoreCard 
                    title="Answer Relevance" 
                    score={dashboardData.mock_response.relevance} 
                    icon="🎯" 
                    delay={700}
                  />
                  <ScoreCard 
                    title="Overall Score" 
                    score={dashboardData.mock_response.total_marks} 
                    icon="🏆" 
                    delay={800}
                  />
                </>
              )}
            </div>

            {/* Feedback Sections */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Resume Feedback */}
              {dashboardData.resume_analysis?.feedback && (
                <FeedbackSection
                  title="Resume Improvements"
                  items={dashboardData.resume_analysis.feedback}
                  bgColor="bg-gradient-to-br from-blue-50 to-indigo-100"
                  icon="📄"
                  textColor="text-blue-800"
                />
              )}

              {/* Interview Feedback */}
              {dashboardData.mock_response?.feedback && (
                <FeedbackSection
                  title="Interview Tips"
                  items={dashboardData.mock_response.feedback}
                  bgColor="bg-gradient-to-br from-green-50 to-emerald-100"
                  icon="🎤"
                  textColor="text-green-800"
                />
              )}

              {/* Gap Fixer Summary */}
              {dashboardData.gap_fixer?.summary && (
                <FeedbackSection
                  title="Overall Assessment"
                  items={dashboardData.gap_fixer.summary}
                  bgColor="bg-gradient-to-br from-purple-50 to-pink-100"
                  icon="📊"
                  textColor="text-purple-800"
                />
              )}

              {/* Improvements */}
              {dashboardData.gap_fixer?.improvements && (
                <FeedbackSection
                  title="Key Improvements"
                  items={dashboardData.gap_fixer.improvements}
                  bgColor="bg-gradient-to-br from-yellow-50 to-orange-100"
                  icon="🚀"
                  textColor="text-orange-800"
                />
              )}
            </div>

            {/* Resource Links */}
            {dashboardData.gap_fixer?.links && dashboardData.gap_fixer.links.length > 0 && (
              <div className="bg-white rounded-2xl p-8 shadow-xl">
                <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                  🔗 Helpful Resources
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {dashboardData.gap_fixer.links.map((link, idx) => (
                    <a
                      key={idx}
                      href={link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block p-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-300 transform hover:scale-105 shadow-lg"
                    >
                      <div className="flex items-center gap-2">
                        <span>🌐</span>
                        <span className="font-medium">Resource {idx + 1}</span>
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Action Button */}
            <div className="text-center">
              <button
                className="py-4 px-12 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-2xl font-bold text-xl hover:from-purple-700 hover:to-blue-700 transform hover:scale-105 transition-all duration-300 shadow-2xl"
                onClick={handleRestart}
              >
                🔄 Start New Interview Practice
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}