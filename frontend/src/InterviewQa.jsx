import { useState } from "react";

export default function InterviewQAGenerator() {
  const [file, setFile] = useState(null);
  const [jd, setJd] = useState("");
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [feedback, setFeedback] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1); // 1: Upload, 2: Questions, 3: Feedback

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
    formData.append("candidate_response", ""); // Required by backend but unused

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
        setFeedback(null);
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
    if (!sessionId) {
      alert("Session expired. Please generate questions again.");
      return;
    }

    // Check if at least one answer is provided
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
        setFeedback(data.feedback || {});
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
    setFeedback(null);
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-2">
            🎯 AI Interview Coach
          </h1>
          <p className="text-gray-600">Master your behavioral interviews with AI-powered feedback</p>
        </div>

        {/* Progress Steps */}
        <div className="flex justify-center mb-8">
          <div className="flex items-center space-x-4">
            <div className={`flex items-center justify-center w-10 h-10 rounded-full ${step >= 1 ? 'bg-purple-600 text-white' : 'bg-gray-300 text-gray-600'}`}>
              1
            </div>
            <div className={`w-16 h-1 ${step >= 2 ? 'bg-purple-600' : 'bg-gray-300'}`}></div>
            <div className={`flex items-center justify-center w-10 h-10 rounded-full ${step >= 2 ? 'bg-purple-600 text-white' : 'bg-gray-300 text-gray-600'}`}>
              2
            </div>
            <div className={`w-16 h-1 ${step >= 3 ? 'bg-purple-600' : 'bg-gray-300'}`}></div>
            <div className={`flex items-center justify-center w-10 h-10 rounded-full ${step >= 3 ? 'bg-purple-600 text-white' : 'bg-gray-300 text-gray-600'}`}>
              3
            </div>
          </div>
        </div>

        {/* Step 1: Upload and Generate */}
        {step === 1 && (
          <div className="bg-white rounded-xl shadow-lg p-8 mb-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
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
                    className="w-full p-3 border-2 border-dashed border-purple-300 rounded-lg hover:border-purple-400 focus:border-purple-500 focus:outline-none transition-colors"
                  />
                  {file && (
                    <div className="mt-2 text-sm text-green-600 flex items-center">
                      ✅ {file.name}
                    </div>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Job Description:
                </label>
                <textarea
                  className="w-full border-2 border-gray-300 rounded-lg p-3 focus:border-purple-500 focus:outline-none transition-colors resize-none"
                  rows={8}
                  value={jd}
                  onChange={handleJdChange}
                  placeholder="Paste the job description here..."
                />
              </div>

              <button
                className={`w-full py-3 px-6 rounded-lg font-semibold text-white transition-all duration-200 ${
                  loading 
                    ? 'bg-gray-400 cursor-not-allowed' 
                    : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 transform hover:scale-105'
                }`}
                onClick={handleGenerate}
                disabled={loading}
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
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
            <div className="bg-white rounded-xl shadow-lg p-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
                💭 Interview Questions
              </h2>
              
              <div className="space-y-6">
                {questions.map((q, idx) => (
                  <div key={idx} className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border-l-4 border-purple-500">
                    <p className="text-lg font-semibold text-gray-800 mb-3">
                      {idx + 1}. {q}
                    </p>
                    <textarea
                      className="w-full border-2 border-gray-300 rounded-lg p-3 focus:border-purple-500 focus:outline-none transition-colors resize-none"
                      rows={4}
                      value={answers[idx] || ""}
                      onChange={(e) => handleAnswerChange(idx, e.target.value)}
                      placeholder="Share your experience and insights here..."
                    />
                  </div>
                ))}

                <div className="flex space-x-4">
                  <button
                    className="flex-1 py-3 px-6 bg-gray-500 text-white rounded-lg font-semibold hover:bg-gray-600 transition-colors"
                    onClick={handleRestart}
                  >
                    ← Start Over
                  </button>
                  <button
                    className={`flex-1 py-3 px-6 rounded-lg font-semibold text-white transition-all duration-200 ${
                      loading 
                        ? 'bg-gray-400 cursor-not-allowed' 
                        : 'bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 transform hover:scale-105'
                    }`}
                    onClick={handleSubmitAnswers}
                    disabled={loading}
                  >
                    {loading ? (
                      <div className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Evaluating...
                      </div>
                    ) : (
                      "📊 Get Feedback"
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Feedback */}
        {step === 3 && feedback && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-lg p-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
                🎯 Your Interview Performance
              </h2>

              {/* Score Cards */}
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                {feedback.tone && (
                  <div className={`p-4 rounded-lg border-2 ${getScoreBg(feedback.tone)}`}>
                    <div className="text-center">
                      <div className={`text-2xl font-bold ${getScoreColor(feedback.tone)}`}>
                        {feedback.tone}/100
                      </div>
                      <div className="text-sm font-semibold text-gray-700">Tone</div>
                    </div>
                  </div>
                )}
                
                {feedback.confidence && (
                  <div className={`p-4 rounded-lg border-2 ${getScoreBg(feedback.confidence)}`}>
                    <div className="text-center">
                      <div className={`text-2xl font-bold ${getScoreColor(feedback.confidence)}`}>
                        {feedback.confidence}/100
                      </div>
                      <div className="text-sm font-semibold text-gray-700">Confidence</div>
                    </div>
                  </div>
                )}
                
                {feedback.relevance && (
                  <div className={`p-4 rounded-lg border-2 ${getScoreBg(feedback.relevance)}`}>
                    <div className="text-center">
                      <div className={`text-2xl font-bold ${getScoreColor(feedback.relevance)}`}>
                        {feedback.relevance}/100
                      </div>
                      <div className="text-sm font-semibold text-gray-700">Relevance</div>
                    </div>
                  </div>
                )}
                
                {feedback.total_marks && (
                  <div className={`p-4 rounded-lg border-2 ${getScoreBg(feedback.total_marks)}`}>
                    <div className="text-center">
                      <div className={`text-3xl font-bold ${getScoreColor(feedback.total_marks)}`}>
                        {feedback.total_marks}/100
                      </div>
                      <div className="text-sm font-semibold text-gray-700">Overall</div>
                    </div>
                  </div>
                )}
              </div>

              {/* Feedback Tips */}
              {feedback.feedback && feedback.feedback.length > 0 && (
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border-l-4 border-blue-500">
                  <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
                    💡 Improvement Tips
                  </h3>
                  <ul className="space-y-3">
                    {feedback.feedback.map((tip, idx) => (
                      <li key={idx} className="flex items-start">
                        <span className="text-blue-500 mr-2 mt-1">•</span>
                        <span className="text-gray-700">{tip}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Additional feedback fields */}
              {feedback.strengths && (
                <div className="bg-green-50 rounded-lg p-6 border-l-4 border-green-500">
                  <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
                    ✅ Strengths
                  </h3>
                  <p className="text-gray-700">{feedback.strengths}</p>
                </div>
              )}

              {feedback.areas_for_improvement && (
                <div className="bg-yellow-50 rounded-lg p-6 border-l-4 border-yellow-500">
                  <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
                    📈 Areas for Improvement
                  </h3>
                  <p className="text-gray-700">{feedback.areas_for_improvement}</p>
                </div>
              )}

              {feedback.overall_feedback && (
                <div className="bg-purple-50 rounded-lg p-6 border-l-4 border-purple-500">
                  <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
                    📝 Overall Feedback
                  </h3>
                  <p className="text-gray-700">{feedback.overall_feedback}</p>
                </div>
              )}

              <div className="mt-8 text-center">
                <button
                  className="py-3 px-8 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transform hover:scale-105 transition-all duration-200"
                  onClick={handleRestart}
                >
                  🔄 Start New Interview Practice
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}