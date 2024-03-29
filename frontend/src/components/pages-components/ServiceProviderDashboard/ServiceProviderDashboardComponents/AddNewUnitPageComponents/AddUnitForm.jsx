import React from "react";
import {
  MdLocationCity,
  MdDriveFileRenameOutline,
  MdPriceCheck,
  MdOutlineDescription,
} from "react-icons/md";
import { BiTimeFive } from "react-icons/bi";
import { useSelector, useDispatch } from "react-redux";
import AddUnitLocation from "./AddUnitLocation";
import { useState } from "react";
import { createStorageUnit } from "../../../../actions/storageUnitActions";

const AddUnitForm = ({ onLocationChange }) => {
  const { serviceProvider } = useSelector((state) => state.getServiceProvider);

  const [formData, setFormData] = useState({
    name: "",
    location: "",
    storage_provider_ids: serviceProvider.id,
    working_hours: "",
    access_hours: "",
    is_online: true,
    description: "",
    address: "",
  });

  const [startingTime, setStartingTime] = useState("");
  const [endingTime, setEndingTime] = useState("");

  const [accessStartingTime, setAccessStartingTime] = useState("");
  const [accessEndingTime, setAccessEndingTime] = useState("");

  const dispatch = useDispatch();

  const getLocationData = (data, id) => {
    if (!data) {
      return setFormData((prev) => {
        return {
          ...prev,
          [id]: "",
        };
      });
    }
    onLocationChange(data);
    let locationData = {
      address: data.properties.formatted || "",
      city: data.properties.city || "",
      country: data.properties.country || "",
      country_code: data.properties.country_code || "",
      county: data.properties.county || "",
      postcode: data.properties.postcode || 0,
      district: data.properties.district || null,
      lat: data.properties.lat,
      lon: data.properties.lon,
    };
    setFormData((prev) => {
      return {
        ...prev,
        [id]: locationData,
      };
    });
  };

  const changeDataHandler = (e) => {
    setFormData((prev) => {
      return {
        ...prev,
        [e.target.id]: e.target.value,
      };
    });
  };

  const startingTimeHandler = (e) => {
    let startingTime = e.target.value;
    setStartingTime(startingTime + "am");
  };

  const endingTimeHandler = (e) => {
    let endingTime = e.target.value;
    setEndingTime(endingTime + "pm");
  };

  const submitFormHandler = (e) => {
    e.preventDefault();
    formData.working_hours = `${startingTime}-${endingTime}`;
    formData.access_hours = `${accessStartingTime}-${accessEndingTime}`;
    formData.address = formData.location.address;
    console.log(formData);
    dispatch(createStorageUnit(formData));
  };

  return (
    <div>
      <h5>Add Storage Facility Form</h5>
      <form onSubmit={submitFormHandler}>
        <div className="form-group">
          <label htmlFor="name">Name</label>
          <div className="input-group">
            <span className="input-group-text">
              <MdDriveFileRenameOutline size={20} />
            </span>

            <input
              type="text"
              name="name"
              id="name"
              className="form-control"
              onChange={changeDataHandler}
              placeholder="Storage Facility Name"
            />
          </div>
        </div>
        <div className="form-group">
          <label htmlFor="location">Location</label>
          <div className="input-group ">
            <span className="input-group-text">
              <MdLocationCity size={20} />
            </span>

            <div className="form-control p-0">
              <AddUnitLocation
                id="location"
                getLocationData={getLocationData}
              />
            </div>
          </div>
        </div>

        <div className="row">
          <div className="col-md-6">
            <div className="form-group">
              <label htmlFor="working_hours">Starting Work Time</label>
              <div className="input-group ">
                <span className="input-group-text">
                  <BiTimeFive size={20} />
                </span>
                <input
                  type="time"
                  className="form-control"
                  placeholder="Select Starting Time"
                  onChange={startingTimeHandler}
                  required
                />
              </div>
            </div>
          </div>

          <div className="col-md-6">
            <div className="form-group">
              <label htmlFor="working_hours">Ending Work Time</label>
              <div className="input-group ">
                <span className="input-group-text">
                  <BiTimeFive size={20} />
                </span>
                <input
                  type="time"
                  className="form-control"
                  placeholder="Select Starting Time"
                  onChange={endingTimeHandler}
                  required
                />
              </div>
            </div>
          </div>
        </div>

        <div className="row">
          <div className="col-md-6">
            <div className="form-group">
              <label htmlFor="working_hours">Starting Access Time</label>
              <div className="input-group ">
                <span className="input-group-text">
                  <BiTimeFive size={20} />
                </span>
                <input
                  type="time"
                  className="form-control"
                  onChange={(e) => setAccessStartingTime(`${e.target.value}am`)}
                  required
                />
              </div>
            </div>
          </div>

          <div className="col-md-6">
            <div className="form-group">
              <label htmlFor="working_hours">Ending Access Time</label>
              <div className="input-group ">
                <span className="input-group-text">
                  <BiTimeFive size={20} />
                </span>
                <input
                  type="time"
                  className="form-control"
                  onChange={(e) => setAccessEndingTime(`${e.target.value}pm`)}
                  required
                />
              </div>
            </div>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="description">Description</label>
          <div className="input-group ">
            <span className="input-group-text">
              <MdOutlineDescription size={20} />
            </span>

            <textarea
              id="description"
              className="form-control"
              cols="30"
              rows="7"
              onChange={changeDataHandler}
            ></textarea>
          </div>
        </div>

        <button type="submit" className="btn btn-dark mt-2">
          CREATE NEW FACILITY
        </button>
      </form>
    </div>
  );
};

export default AddUnitForm;
