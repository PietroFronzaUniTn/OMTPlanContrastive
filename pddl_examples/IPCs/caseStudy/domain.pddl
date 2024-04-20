(define (domain gripper-strips)
(:requirements :strips)
   (:predicates (room ?r)
		(ball ?b)
		(gripper ?g)
		(at-robby ?r)
		(not-broken ?g)
		(at ?b ?r)
		(free ?g)
		(carry ?o ?g))

   (:action move
       :parameters  (?from ?to)
       :precondition (and  (room ?from) (room ?to) (at-robby ?from))
       :effect (and  (at-robby ?to)
		     (not (at-robby ?from))))



   (:action pick
       :parameters (?obj ?room ?gripper)
       :precondition  (and  (ball ?obj) (room ?room) (gripper ?gripper) (not-broken ?gripper)
			    (at ?obj ?room) (at-robby ?room) (free ?gripper))
       :effect (and (carry ?obj ?gripper)
		    (not (at ?obj ?room)) 
		    (not (free ?gripper))))
		    

   (:action drop
       :parameters  (?obj  ?room ?gripper)
       :precondition  (and  (ball ?obj) (room ?room) (gripper ?gripper) (not-broken ?gripper)
			    (carry ?obj ?gripper) (at-robby ?room))
       :effect (and (at ?obj ?room)
		    (free ?gripper)
		    (not (carry ?obj ?gripper))
		    ))
		    
		    

		    
		    
	(:action drop-both
      :parameters  (?obj1 ?obj2 ?room ?gripper1 ?gripper2)
      :precondition  (and  (ball ?obj1) (ball ?obj2) (room ?room) (gripper ?gripper1) (gripper ?gripper2) (not-broken ?gripper1) (not-broken ?gripper2)
			    (carry ?obj1 ?gripper1) (carry ?obj2 ?gripper2) (at-robby ?room))
      :effect (and (at ?obj1 ?room) (at ?obj2 ?room)
		    (free ?gripper1) (free ?gripper2)
		    (not (carry ?obj1 ?gripper1))
		    (not (carry ?obj2 ?gripper2)))))


