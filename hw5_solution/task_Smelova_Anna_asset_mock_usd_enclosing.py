def side_effect():
        iter = -1

        def get_course():
            nonlocal iter
            iter += 1
            usd_course = 76.32 + 0.1 * iter
            return float(usd_course)

        return get_course

mock_get_usd_course.side_effect = side_effect()