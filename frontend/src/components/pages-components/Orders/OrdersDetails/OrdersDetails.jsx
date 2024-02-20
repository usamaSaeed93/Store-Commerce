import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { FaFacebook } from "react-icons/fa";
import { FaInstagram, FaTwitter, FaGoogle } from "react-icons/fa";
import Container from "../../../shared-components/container/Container";

import {
  getOrderDetailsAdmin,
  updateOrderAdmin,
  getOrderDetails,
} from "../../../actions/ordersActions";
import Spinner from "../../../shared-components/Spinner/Spinner";
import { UPDATE_ORDERS_ADMIN_RESET } from "../../../constants/ordersConstants";
import { toast } from "react-toastify";
import OrderStatusUpdate from "../OrderStatusUpdate/OrderStatusUpdate";

const OrdersDetails = () => {
  const { id } = useParams();
  const { info } = useSelector((state) => state.userInfo);

  const { loading, order, error } = useSelector(
    (state) => state.orderDetailsAdmin
  );

  const {
    loading: loading_user,
    order: order_user,
    error: error_user,
  } = useSelector((state) => state.orderDetails);
  const isServiceProvider = info && info.is_service_provider;
  const loadingSelector = isServiceProvider ? loading : loading_user;
  const { loading: updateLoading, order: updateOrder } = useSelector(
    (state) => state.updateOrderAdmin
  );
  const [componentLoading, setcomponentLoading] = useState();
  const [formData, setFormData] = useState({
    pending: order && order.pending,
    proccess: order && order.proccess,
    completed: order && order.completed,
  });

  const dispatch = useDispatch();

  const navigate = useNavigate();

const statusStyles={
    width:"95px",
    justifyContent:"center",
    display:"flex"
}

  useEffect(() => {
    if (info && info.is_service_provider) {
  
      dispatch(getOrderDetailsAdmin(id));
      if (updateOrder) {
        navigate("/service-provider-dashboard/analytics");
        toast.success("Updated");
        dispatch({ type: UPDATE_ORDERS_ADMIN_RESET });
      }
    } else {
   
      dispatch(getOrderDetailsAdmin(id));
      dispatch(getOrderDetails(id));
    }
  }, [dispatch, updateOrder]);

  return (
    <div className="py-5">
      {loadingSelector || updateLoading ? (
        <Spinner />
      ) : (
        <div className="container">
          <h1>
            Order <span className="mineTextOrange">Details of ID: {id}</span>
          </h1>

          <div className="row mt-3">
            <div className="col-md-6 col-lg-8">
              <div className="border-bottom py-2">
                <h3>Person's Details</h3>
                <div>
                  <span className="fw-bold me-2">Email:</span>
                  <span>{order?.user?.email || info?.email}</span>
                </div>
              </div>
              {/* <div className="border-bottom py-2">
                <h3>Payments Details</h3>
                <p className="lead">Method: PayPal</p>
                {isPaid ? (
                  <div className="alert alert-success" role="alert">
                    Paid
                  </div>
                ) : (
                  <div className="alert alert-danger" role="alert">
                    Not Paid
                  </div>
                )}
              </div> */}
              {info && info.is_service_provider ? (
                <div>
                  <div className="col-md-12">
                    <div className="">
                      <div className="card-body">
                        <ul className="list-group list-group-flush">
                          <li className="list-group-item">
                            <h5>Facility Information</h5>
                          </li>

                          <li className="list-group-item">
                            <h6>Facilty Details</h6>
                          </li>
                          <li className="list-group-item d-flex justify-content-between">
                            <p className="fw-bold">Provider Name</p>
                            <p>{order?.unit_order?.storage_facility?.name}</p>
                          </li>
                          <li className="list-group-item">
                            <div className="d-flex justify-content-between">
                              <span className="fw-bold me-2">Email</span>
                              <span>
                                {
                                  order?.unit_order?.storage_facility
                                    .storage_provider.email
                                }
                              </span>
                            </div>
                          </li>
                          <li className="list-group-item">
                            <div className=" d-flex justify-content-between">
                              <span className="fw-bold me-2">Phone Number</span>
                              <span>
                                {
                                  order?.unit_order?.storage_facility
                                    .storage_provider.phone_number
                                }
                              </span>
                            </div>
                          </li>
                          <li className="list-group-item">
                            <div className=" d-flex justify-content-between">
                              <span className="fw-bold me-2">Fax Number</span>
                              <span>
                                {
                                  order?.unit_order?.storage_facility
                                    .storage_provider.fax_number
                                }
                              </span>
                            </div>
                          </li>

                          <li className="list-group-item d-flex justify-content-between">
                            <p className="fw-bold">Website</p>
                            <p>
                              {
                                order?.unit_order?.storage_facility
                                  .storage_provider.website
                              }
                            </p>
                          </li>
                          <li className="list-group-item d-flex justify-content-between">
                            <p className="fw-bold">Working Hours</p>
                            <p>
                              {
                                order?.unit_order?.storage_facility
                                  .working_hours
                              }
                            </p>
                          </li>
                          <div className="d-flex justify-content-start align-items-center gap-3 my-3">
                            {order?.unit_order?.storage_facility.storage_provider
                              .facebook ? (
                              <span>
                                <Link
                                  to={
                                    order?.unit_order?.storage_facility
                                      .storage_provider.facebook
                                  }
                                >
                                  <FaFacebook size={32} />
                                </Link>
                              </span>
                            ) : (
                              ""
                            )}

                            {order?.unit_order?.storage_facility
                              .storage_provider.instagram ? (
                              <span>
                                <Link
                                  to={
                                    order?.unit_order?.storage_facility
                                      .storage_provider.instagram
                                  }
                                >
                                  <FaInstagram size={32} />
                                </Link>
                              </span>
                            ) : (
                              ""
                            )}
                            {order?.unit_order?.storage_facility
                              .storage_provider.twitter ? (
                              <span>
                                <Link
                                  to={
                                    order?.unit_order?.storage_facility
                                      .storage_provider.twitter
                                  }
                                >
                                  <FaTwitter size={32} />
                                </Link>
                              </span>
                            ) : (
                              ""
                            )}
                            {order?.unit_order?.storage_facility
                              .storage_provider.google_business ? (
                              <span>
                                <Link
                                  to={
                                    order?.unit_order?.storage_facility
                                      .storage_provider.google_business
                                  }
                                >
                                  <FaGoogle size={32} />
                                </Link>
                              </span>
                            ) : (
                              ""
                            )}
                          </div>
                        </ul>

                        <div className=""></div>
                      </div>
                    </div>
                  </div>
                  <div className="border-bottom py-2">
                    <h3>Order Status</h3>
                    <p className="lead">Pending</p>
                    {order.pending ? (
                      <div className="alert alert-success" role="alert">
                        Done
                      </div>
                    ) : (
                      <div className="alert alert-danger" role="alert">
                      Pending
                      </div>
                    )}
                    <p className="lead">Processing</p>
                    {order.proccess ? (
                      <div className="alert alert-success" role="alert">
                        Processing Completed
                      </div>
                    ) : (
                      <div className="alert alert-danger" role="alert">
                         Processing
                      </div>
                    )}

                    <p className="lead">Completed</p>
                    {order.completed ? (
                      <div className="alert alert-success" role="alert">
                        Order Completed
                      </div>
                    ) : (
                      <div className="alert alert-danger" role="alert">
                        Not Completed
                      </div>
                    )}

                    <p className="lead">Is Paid</p>
                    {order.payment_done ? (
                      <div className="alert alert-success" role="alert">
                        Paid
                      </div>
                    ) : (
                      <div className="alert alert-danger" role="alert">
                        Not Paid
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="col-md-12">
                  <div className="">
                    <div className="card-body">
                      <ul className="list-group list-group-flush">
                        <li className="list-group-item">
                          <h5>Facility Provider Information</h5>
                        </li>

                        <li className="list-group-item">
                          <h6>Facilty Details</h6>
                        </li>
                        <li className="list-group-item d-flex justify-content-between">
                          <p className="fw-bold">Provider Name</p>
                          <p>{order_user?.unit_order?.storage_facility?.name}</p>
                        </li>
                        <li className="list-group-item">
                          <div className="d-flex justify-content-between">
                            <span className="fw-bold me-2">Email</span>
                            <span>
                              {
                                order_user?.unit_order?.storage_facility
                                  .storage_provider.email
                              }
                            </span>
                          </div>
                        </li>
                        <li className="list-group-item">
                          <div className=" d-flex justify-content-between">
                            <span className="fw-bold me-2">Phone Number</span>
                            <span>
                              {
                                order_user?.unit_order?.storage_facility
                                  .storage_provider.phone_number
                              }
                            </span>
                          </div>
                        </li>
                        <li className="list-group-item">
                          <div className=" d-flex justify-content-between">
                            <span className="fw-bold me-2">Fax Number</span>
                            <span>
                              {
                                order_user?.unit_order?.storage_facility
                                  .storage_provider.fax_number
                              }
                            </span>
                          </div>
                        </li>
                        <li className="list-group-item d-flex justify-content-between">
                          <p className="fw-bold">Website</p>
                          <p>
                            {
                              order_user?.unit_order?.storage_facility
                                .storage_provider.website
                            }
                          </p>
                        </li>
                        <li className="list-group-item d-flex justify-content-between">
                          <p className="fw-bold">Working Hours</p>
                          <p>
                            {
                              order_user?.unit_order?.storage_facility
                                .working_hours
                            }
                          </p>
                        </li>
                        <div className="d-flex justify-content-start align-items-center gap-3 my-3">
                          {order_user?.unit_order?.storage_facility
                            .storage_provider.facebook ? (
                            <span>
                              <Link
                                to={
                                  order?.unit_order?.storage_facility
                                    .storage_provider.facebook
                                }
                              >
                                <FaFacebook size={32} />
                              </Link>
                            </span>
                          ) : (
                            ""
                          )}

                          {order_user?.unit_order?.storage_facility
                            .storage_provider.instagram ? (
                            <span>
                              <Link
                                to={
                                  order?.unit_order?.storage_facility
                                    .storage_provider.instagram
                                }
                              >
                                <FaInstagram size={32} />
                              </Link>
                            </span>
                          ) : (
                            ""
                          )}
                          {order_user?.unit_order?.storage_facility
                            .storage_provider.twitter ? (
                            <span>
                              <Link
                                to={
                                  order?.unit_order?.storage_facility
                                    .storage_provider.twitter
                                }
                              >
                                <FaTwitter size={32} />
                              </Link>
                            </span>
                          ) : (
                            ""
                          )}
                          {order_user?.unit_order?.storage_facility
                            .storage_provider.google_business ? (
                            <span>
                              <Link
                                to={
                                  order?.unit_order?.storage_facility
                                    .storage_provider.google_business
                                }
                              >
                                <FaGoogle size={32} />
                              </Link>
                            </span>
                          ) : (
                            ""
                          )}
                        </div>
                      </ul>

                      <div className=""></div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {info && info.is_service_provider ? (
              <div className="col-md-6 col-lg-4">
                <div className="card">
                  <div className="card-body">
                    <ul className="list-group list-group-flush">
                      <li className="list-group-item">
                        <h5>Order Summary</h5>
                      </li>

                      <li className="list-group-item">
                        <h6>Storage Unit Details</h6>
                      </li>
                      <li className="list-group-item d-flex justify-content-between">
                        <p className="fw-bold">Name</p>
                        <p>{order?.unit_order?.name}</p>
                      </li>
                      <li className="list-group-item">
                        <div>
                          <span className="fw-bold me-2">Description:</span>
                          <span>{order?.unit_order?.description}</span>
                        </div>
                      </li>
                      <li className="list-group-item d-flex justify-content-between">
                        <p className="fw-bold">Price</p>
                        <p>${order?.unit_order?.per_unit_price}</p>
                      </li>
                    </ul>

                    <div>
                      <h5>Update Order Details</h5>
                      <OrderStatusUpdate
                        id={id}
                        updateOrderAdmin={updateOrderAdmin}
                        dispatch={dispatch}
                        order={order}
                      />
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="col-md-6 col-lg-4">
                <div className="card">
                  <div className="card-body">
                    <ul className="list-group list-group-flush">
                      <li className="list-group-item">
                        <h5>Order Summary</h5>
                      </li>

                      <li className="list-group-item">
                        <h6>Storage Unit Details</h6>
                      </li>
                      <li className="list-group-item d-flex justify-content-between">
                        <p className="fw-bold">Name</p>
                        <p>{order_user?.unit_order?.name}</p>
                      </li>
                      <li className="list-group-item ">
                        <div className=" d-flex justify-content-between">
                          <span className="fw-bold me-2">Location</span>
                          <span>
                            {order_user?.unit_order?.storage_facility.address}
                          </span>
                        </div>
                      </li>
                      <li className="list-group-item">
                        <div className=" d-flex justify-content-between">
                          <span className="fw-bold me-2">Access Hours</span>
                          <span>
                            {
                              order_user?.unit_order?.storage_facility
                                .access_hours
                            }
                          </span>
                        </div>
                      </li>
                      <li className="list-group-item d-flex justify-content-between">
                        <p className="fw-bold">Price</p>
                        <p>${order_user?.unit_order?.per_unit_price}</p>
                      </li>
                      <li className="list-group-item d-flex justify-content-between">
                        <p className="fw-bold">Storage Unit Type</p>
                        <p>
                          {order_user?.unit_order?.storage_unit_type?.title}
                        </p>
                      </li>
                      <li className="list-group-item d-flex justify-content-between">
                        <p className="fw-bold">Pending</p>
                        {order_user.pending ? (
                          <div className="alert alert-success " role="alert" style={statusStyles}>
                            Done
                          </div>
                        ) : (
                          <div className="alert alert-danger" role="alert">
                            Pending
                          </div>
                        )}
                      </li>
                      <li className="list-group-item d-flex justify-content-between">
                        <p className="fw-bold">Process</p>
                        {order_user.proccess ? (
                          <div className="alert alert-success "  role="alert" style={statusStyles}>
                            Done
                          </div>
                        ) : (
                          <div className="alert alert-danger " role="alert">
                          Pending
                          </div>
                        )}
                      </li>
                      <li className="list-group-item d-flex justify-content-between">
                        <p className="fw-bold">Completed</p>
                        {order_user.completed ? (
                          <div className="alert alert-success" role="alert" style={statusStyles}>
                            Done
                          </div>
                        ) : (
                          <div className="alert alert-danger" role="alert">
                            Pending
                          </div>
                        )}
                      </li>
                    </ul>

                    <div>
                     
                      <ul className="list-group list-group-flush">
                        <li className="list-group-item d-flex justify-content-between">
                          <p className="fw-bold">Total Price : </p>
                          <p className="fw-bold">${order_user?.unit_order?.per_unit_price} </p>
                        </li>
                      </ul>
                      {/* <OrderStatusUpdate
                        id={id}
                        updateOrderAdmin={updateOrderAdmin}
                        dispatch={dispatch}
                        order={order}
                      /> */}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default OrdersDetails;
