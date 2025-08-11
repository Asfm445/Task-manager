import { useState } from "react";
import Form from "../components/form";

function Register() {
  localStorage.clear();
  const [inputs, setInputs] = useState({
    username: "",
    email: "",
    password: "",
  });

  return (
    <Form
      type={"Register"}
      inputs={inputs}
      setInputs={setInputs}
      apiUrl={"api/user/register/"}
    ></Form>
  );
}

export default Register;
