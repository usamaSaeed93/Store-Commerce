import React, { useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import Container from "../../shared-components/container/Container";
import HomeOrdersTable from "../Home/HomeOrdersTable/HomeOrdersTable";
import Spinner from "../../shared-components/Spinner/Spinner";
import { getAllOrders } from "../../actions/ordersActions";

const Orders = () => {
  const { info } = useSelector((state) => state.userInfo);
  const allOrdersAdmin = useSelector((state) => state.allOrdersAdmin);
  const allOrders = useSelector((state) => state.allOrders);

  // Check if the user is a service provider
  const isServiceProvider = info && info.is_service_provider;

  // Select the appropriate orders slice based on the user type
  const order = isServiceProvider ? allOrdersAdmin : allOrders;
  const {orders,loading} = order;
  const dispatch = useDispatch();

  // Side Effects
  useEffect(() => {
    dispatch(getAllOrders());
  }, [dispatch]);

  return (
    <div className="py-5">
      <Container>
        <h1>
          My <span className="mineTextOrange">Orders</span>
        </h1>
        {loading ? (
          <Spinner />
        ) : (
          <>
       {   
            orders? ( orders?.length === 0 ? (
              <h5 className="text-center">You have no Orders</h5>
            ) : (
              <>
                <HomeOrdersTable orders={orders} />
              </>
            )) : <p className="p-3  text-black rounded">No Orders</p>
          
           }
          </>
        )}
      </Container>
    </div>
  );
};

export default Orders;
