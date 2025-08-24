import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { checkIsAuthorized } from "../authorize";

function ProtectedRoute({ children }) {
  const [isAuthorized, setIsAuthorized] = useState(null);

  useEffect(() => {
    const verifyAuthorization = async () => {
      const tempIsAuthorized = await checkIsAuthorized();
      setIsAuthorized(tempIsAuthorized);
    };

    verifyAuthorization();
  }, []);

  if (isAuthorized === null) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="w-12 h-12 border-4 border-blue-500 border-dashed rounded-full animate-spin"></div>
      </div>
    );
  }

  return isAuthorized ? children : <Navigate to="/login" />;
}

export default ProtectedRoute;
