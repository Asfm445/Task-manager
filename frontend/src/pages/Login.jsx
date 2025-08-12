import { useState } from "react";
import Form from "../components/form";

function Login() {
  const [inputs, setInputs] = useState({
    email: "",
    password: "",
  });
  return (
    <Form
      type={"Login"}
      inputs={inputs}
      setInputs={setInputs}
      apiUrl={"auth/token"}
    ></Form>
  );
}

export default Login;
