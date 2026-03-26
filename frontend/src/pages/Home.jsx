import { CheckCircle2, Clock, LayoutDashboard, LineChart, Target, Users } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

export default function Home() {
    const navigate = useNavigate();
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem("access_token");
        setIsLoggedIn(!!token);
    }, []);

    const features = [
        {
            icon: <Target className="w-8 h-8" />,
            title: "Smart Task Management",
            description: "Create, organize, and track tasks with subtasks, priorities, and deadlines. Stay on top of everything that matters."
        },
        {
            icon: <Clock className="w-8 h-8" />,
            title: "Time Tracking",
            description: "Monitor time spent on tasks with built-in progress tracking. Know exactly where your time goes."
        },
        {
            icon: <Users className="w-8 h-8" />,
            title: "Team Collaboration",
            description: "Assign tasks to team members, share progress, and work together seamlessly on projects."
        },
        {
            icon: <LayoutDashboard className="w-8 h-8" />,
            title: "Daily Planning",
            description: "Plan your day efficiently with our intuitive day planner. Organize tasks by time slots and priorities."
        },
        {
            icon: <LineChart className="w-8 h-8" />,
            title: "Analytics & Insights",
            description: "Get detailed analytics on task completion, time efficiency, and productivity trends."
        },
        {
            icon: <CheckCircle2 className="w-8 h-8" />,
            title: "Repetitive Tasks",
            description: "Set up recurring tasks that automatically reset. Perfect for daily routines and habits."
        }
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
            {/* Navigation */}
            <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center gap-2">
                            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                                <Target className="w-6 h-6 text-white" />
                            </div>
                            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                                TaskMaster
                            </span>
                        </div>
                        <div className="flex items-center gap-3">
                            {isLoggedIn ? (
                                <>
                                    <button
                                        onClick={() => navigate("/tasks")}
                                        className="px-4 py-2 text-gray-700 hover:text-blue-600 font-medium transition-colors"
                                    >
                                        Dashboard
                                    </button>
                                    <button
                                        onClick={() => {
                                            localStorage.clear();
                                            setIsLoggedIn(false);
                                            navigate("/login");
                                        }}
                                        className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all"
                                    >
                                        Logout
                                    </button>
                                </>
                            ) : (
                                <>
                                    <Link
                                        to="/login"
                                        className="px-4 py-2 text-gray-700 hover:text-blue-600 font-medium transition-colors"
                                    >
                                        Login
                                    </Link>
                                    <Link
                                        to="/register"
                                        className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all"
                                    >
                                        Get Started
                                    </Link>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-600/10 via-purple-600/10 to-pink-600/10"></div>
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32 relative">
                    <div className="text-center max-w-4xl mx-auto">
                        <div className="inline-flex items-center gap-2 bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm font-semibold mb-6 animate-pulse">
                            <span className="w-2 h-2 bg-blue-600 rounded-full"></span>
                            Your productivity companion
                        </div>

                        <h1 className="text-5xl md:text-7xl font-extrabold mb-6 leading-tight">
                            <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                                Organize Your Life,
                            </span>
                            <br />
                            <span className="text-gray-900">One Task at a Time</span>
                        </h1>

                        <p className="text-xl md:text-2xl text-gray-600 mb-10 leading-relaxed">
                            The ultimate task management platform that helps you stay organized,
                            track progress, and achieve your goals with powerful analytics and collaboration tools.
                        </p>

                        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                            {isLoggedIn ? (
                                <button
                                    onClick={() => navigate("/tasks")}
                                    className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-bold text-lg hover:shadow-2xl hover:scale-105 transition-all"
                                >
                                    Go to Dashboard
                                </button>
                            ) : (
                                <>
                                    <Link
                                        to="/register"
                                        className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-bold text-lg hover:shadow-2xl hover:scale-105 transition-all"
                                    >
                                        Start Free Today
                                    </Link>
                                    <Link
                                        to="/login"
                                        className="px-8 py-4 bg-white text-gray-800 rounded-xl font-bold text-lg border-2 border-gray-200 hover:border-blue-600 hover:shadow-xl transition-all"
                                    >
                                        Sign In
                                    </Link>
                                </>
                            )}
                        </div>

                        {/* Stats */}
                        <div className="grid grid-cols-3 gap-8 mt-16 max-w-2xl mx-auto">
                            <div>
                                <div className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                                    100%
                                </div>
                                <div className="text-sm text-gray-600 mt-1">Free Forever</div>
                            </div>
                            <div>
                                <div className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                                    ∞
                                </div>
                                <div className="text-sm text-gray-600 mt-1">Unlimited Tasks</div>
                            </div>
                            <div>
                                <div className="text-4xl font-bold bg-gradient-to-r from-pink-600 to-blue-600 bg-clip-text text-transparent">
                                    24/7
                                </div>
                                <div className="text-sm text-gray-600 mt-1">Always Available</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="py-20 bg-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl md:text-5xl font-extrabold text-gray-900 mb-4">
                            Everything You Need to Stay Productive
                        </h2>
                        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                            Powerful features designed to help you manage tasks efficiently and achieve more every day.
                        </p>
                    </div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {features.map((feature, index) => (
                            <div
                                key={index}
                                className="group p-8 bg-gradient-to-br from-white to-gray-50 rounded-2xl border border-gray-200 hover:border-blue-300 hover:shadow-2xl transition-all duration-300 hover:-translate-y-1"
                            >
                                <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center text-white mb-6 group-hover:scale-110 transition-transform">
                                    {feature.icon}
                                </div>
                                <h3 className="text-xl font-bold text-gray-900 mb-3">
                                    {feature.title}
                                </h3>
                                <p className="text-gray-600 leading-relaxed">
                                    {feature.description}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-20 bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 relative overflow-hidden">
                <div className="absolute inset-0 bg-black/10"></div>
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative">
                    <h2 className="text-4xl md:text-5xl font-extrabold text-white mb-6">
                        Ready to Boost Your Productivity?
                    </h2>
                    <p className="text-xl text-white/90 mb-10">
                        Join thousands of users who are already managing their tasks smarter, not harder.
                    </p>
                    {!isLoggedIn && (
                        <Link
                            to="/register"
                            className="inline-block px-10 py-5 bg-white text-blue-600 rounded-xl font-bold text-lg hover:shadow-2xl hover:scale-105 transition-all"
                        >
                            Get Started for Free
                        </Link>
                    )}
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-gray-900 text-white py-12">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex flex-col md:flex-row justify-between items-center">
                        <div className="flex items-center gap-2 mb-4 md:mb-0">
                            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                                <Target className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-lg font-bold">TaskMaster</span>
                        </div>
                        <div className="text-gray-400 text-sm">
                            © 2025 TaskMaster. Built with ❤️ for productivity.
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
}
