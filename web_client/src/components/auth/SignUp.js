import React from "react";
import {
  MDBContainer,
  MDBRow,
  MDBCol,
  MDBBtn,
  MDBCard,
  MDBCardBody,
  MDBInput,
  MDBLink,
} from "mdbreact";
import "../../index.css";
import { Link } from "react-router-dom";

const SignUpPage = () => {
  return (
    <MDBContainer className="my-5 py-5">
      <MDBRow center>
        <MDBCol md="6">
          <MDBCard>
            <div className="header pt-3 unique-color-dark lighten-2">
              <MDBRow className="d-flex justify-content-start">
                <h3 className="text-white font-weight-normal mt-3 mb-4 pb-1 mx-5">Sign Up</h3>
              </MDBRow>
            </div>
            <MDBCardBody className="mx-4 mt-4">
              <MDBInput label="Full Name" group type="text" validate />
              <MDBInput label="Email" group type="text" validate />
              <MDBInput
                label=" Password"
                group
                type="password"
                validate
                containerClass="mb-0"
              />

              <div className="text-center mb-4 mt-5">
                <MDBBtn
                  rounded
                  color="primary"
                  type="button"
                  className="btn-block text-white z-depth-2 unique-color-dark btn-block z-depth-2"
                >
                  Sign Up
                </MDBBtn>
              </div>
              <p className="font-small grey-text d-flex justify-content-center">
                Already have an account?
                <Link
                  to="login"
                  className="dark-grey-text font-weight-bold ml-1"
                >
                  Sign In
                </Link>
              </p>
            </MDBCardBody>
          </MDBCard>
        </MDBCol>
      </MDBRow>
    </MDBContainer>
  );
};

export default SignUpPage;