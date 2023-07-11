; benchmark generated from python API
(set-info :status unknown)
(declare-fun |value(c0)_0| () Real)
(declare-fun |value(c1)_0| () Real)
(declare-fun |rate_value(c0)_0| () Real)
(declare-fun |rate_value(c1)_0| () Real)
(declare-fun |value(c1)_1| () Real)
(declare-fun |value(c0)_1| () Real)
(declare-fun increment_c0_0 () Bool)
(declare-fun increment_c1_0 () Bool)
(declare-fun decrement_c0_0 () Bool)
(declare-fun decrement_c1_0 () Bool)
(declare-fun increase_rate_c0_0 () Bool)
(declare-fun |rate_value(c0)_1| () Real)
(declare-fun increase_rate_c1_0 () Bool)
(declare-fun |rate_value(c1)_1| () Real)
(declare-fun decrement_rate_c0_0 () Bool)
(declare-fun decrement_rate_c1_0 () Bool)
(assert
 (= |value(c0)_0| 0.0))
(assert
 (= |value(c1)_0| 0.0))
(assert
 (= |rate_value(c0)_0| 0.0))
(assert
 (= |rate_value(c1)_0| 0.0))
(assert
 (and (<= (+ |value(c0)_1| 1.0) |value(c1)_1|) (= 0.0 (- |value(c1)_1| 3.0))))
(assert
 (=> increment_c0_0 (>= 4.0 (+ |value(c0)_0| |rate_value(c0)_0|))))
(assert
 (=> increment_c0_0 (= |value(c0)_1| (+ |value(c0)_0| |rate_value(c0)_0|))))
(assert
 (=> increment_c1_0 (>= 4.0 (+ |value(c1)_0| |rate_value(c1)_0|))))
(assert
 (=> increment_c1_0 (= |value(c1)_1| (+ |value(c1)_0| |rate_value(c1)_0|))))
(assert
 (=> decrement_c0_0 (<= 0.0 (- |value(c0)_0| |rate_value(c0)_0|))))
(assert
 (=> decrement_c0_0 (= |value(c0)_1| (- |value(c0)_0| |rate_value(c0)_0|))))
(assert
 (=> decrement_c1_0 (<= 0.0 (- |value(c1)_0| |rate_value(c1)_0|))))
(assert
 (=> decrement_c1_0 (= |value(c1)_1| (- |value(c1)_0| |rate_value(c1)_0|))))
(assert
 (=> increase_rate_c0_0 (>= 10.0 (+ |rate_value(c0)_0| 1.0))))
(assert
 (=> increase_rate_c0_0 (= |rate_value(c0)_1| (+ |rate_value(c0)_0| 1.0))))
(assert
 (=> increase_rate_c1_0 (>= 10.0 (+ |rate_value(c1)_0| 1.0))))
(assert
 (=> increase_rate_c1_0 (= |rate_value(c1)_1| (+ |rate_value(c1)_0| 1.0))))
(assert
 (=> decrement_rate_c0_0 (<= 1.0 |rate_value(c0)_0|)))
(assert
 (=> decrement_rate_c0_0 (= |rate_value(c0)_1| (- |rate_value(c0)_0| 1.0))))
(assert
 (=> decrement_rate_c1_0 (<= 1.0 |rate_value(c1)_0|)))
(assert
 (=> decrement_rate_c1_0 (= |rate_value(c1)_1| (- |rate_value(c1)_0| 1.0))))
(assert
 (or (= |value(c0)_1| |value(c0)_0|) (or increment_c0_0 decrement_c0_0)))
(assert
 (or (= |value(c1)_1| |value(c1)_0|) (or increment_c1_0 decrement_c1_0)))
(assert
 (or (= |rate_value(c0)_1| |rate_value(c0)_0|) (or increase_rate_c0_0 decrement_rate_c0_0)))
(assert
 (or (= |rate_value(c1)_1| |rate_value(c1)_0|) (or increase_rate_c1_0 decrement_rate_c1_0)))
(assert
 ((_ at-most 1) increment_c0_0 increment_c1_0 decrement_c0_0 decrement_c1_0 increase_rate_c0_0 increase_rate_c1_0 decrement_rate_c0_0 decrement_rate_c1_0))
(check-sat)
