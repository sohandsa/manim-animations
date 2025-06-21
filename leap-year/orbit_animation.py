from manim import *

class EarthOrbit(Scene):
    def construct(self):
        # Title
        title = Text("Earth's Orbit, Calendar Drift, and Leap Years", font_size=36)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        # Initial Explanation
        orbit_time_text = Text("Earth's true orbit (solar year) is ~365.25 days.", font_size=28).to_edge(UP)
        calendar_text = Text("A standard calendar year is 365 days.", font_size=28).next_to(orbit_time_text, DOWN)
        discrepancy_text = Text("This ~0.25 day difference causes calendar drift.", font_size=28, color=YELLOW).next_to(calendar_text, DOWN)
        
        self.play(Write(orbit_time_text))
        self.wait(0.5)
        self.play(Write(calendar_text))
        self.wait(0.5)
        self.play(Write(discrepancy_text))
        self.wait(2.5)
        self.play(FadeOut(orbit_time_text), FadeOut(calendar_text), FadeOut(discrepancy_text))
        self.wait(0.5)

        # Sun
        sun = Circle(radius=0.5, color=YELLOW, fill_opacity=1)
        sun_label = Text("Sun", font_size=24).next_to(sun, DOWN, buff=0.1)
        sun_group = VGroup(sun, sun_label).shift(LEFT*0.5) # Shift sun slightly left to make space for drift visuals
        self.play(FadeIn(sun_group))

        # Orbit Path
        orbit_path = Ellipse(width=7.5, height=5.5, color=BLUE_D).rotate(PI/10).shift(LEFT*0.5)
        
        # Calendar Zero Marker (Fixed point for Jan 1st)
        calendar_zero_prop = 0.0
        # Changed GREEN_SCREEN to GREEN
        calendar_zero_marker = Dot(orbit_path.point_from_proportion(calendar_zero_prop), color=GREEN, radius=0.1) 
        calendar_zero_label = Text("Calendar Jan 1st", font_size=18).next_to(calendar_zero_marker, RIGHT, buff=0.1)
        
        # Earth Dot
        earth_dot = Dot(color=BLUE, radius=0.15)
        earth_label = Text("Earth", font_size=20).add_updater(lambda m: m.next_to(earth_dot, UP, buff=0.1))
        
        # Earth's visual orbit driven by this tracker
        earth_orbit_anim_tracker = ValueTracker(calendar_zero_prop) 
        earth_dot.add_updater(lambda m: m.move_to(orbit_path.point_from_proportion(earth_orbit_anim_tracker.get_value() % 1.0)))

        # Year counter and accumulated time visualizer
        year_count = 0
        year_text = Text(f"Year: {year_count}", font_size=28).to_corner(UL)
        
        accumulated_day_label = Text("Calendar Lag:", font_size=22).to_corner(UR).shift(LEFT*2.5 + DOWN*0.2)
        day_bar_outline = Rectangle(width=2, height=0.3, color=WHITE).next_to(accumulated_day_label, DOWN, buff=0.1, aligned_edge=LEFT)
        day_bar_fill = Rectangle(width=0, height=0.3, color=RED, fill_opacity=0.7).align_to(day_bar_outline, LEFT) # Red for lag
        day_bar_fill.move_to(day_bar_outline.get_left(), aligned_edge=LEFT)
        accumulated_time_text = Text("0.00 days", font_size=20).next_to(day_bar_outline, DOWN, buff=0.1, aligned_edge=LEFT)

        self.play(
            Create(orbit_path), FadeIn(year_text), FadeIn(calendar_zero_marker), FadeIn(calendar_zero_label),
            FadeIn(accumulated_day_label), Create(day_bar_outline), Create(day_bar_fill), FadeIn(accumulated_time_text)
        )
        self.add(earth_dot, earth_label) # Add earth after path is created
        earth_dot.move_to(orbit_path.point_from_proportion(calendar_zero_prop)) # Ensure start position

        # Animation parameters
        orbit_duration_per_year = 3.5
        total_years_to_simulate = 5 
        accumulated_fraction = 0.0 # Tracks the 0.25, 0.50, 0.75, 1.0 day lag

        # Temporary mobjects for drift/sync visuals
        # Initialize actual_earth_marker_label here to ensure it's always defined before potential FadeOut
        actual_earth_marker_label = Text("", font_size=16) # Empty text initially
        drift_arc_obj = VMobject()
        actual_earth_marker_obj = VMobject()
        drift_text_obj = VMobject()


        for i in range(total_years_to_simulate):
            year_count += 1
            
            # Animate Earth's main visual orbit (representing 365 calendar days)
            # Earth starts at calendar_zero_marker and completes one visual loop
            target_orbit_prop = earth_orbit_anim_tracker.get_value() + 1.0
            self.play(
                earth_orbit_anim_tracker.animate.set_value(target_orbit_prop),
                Transform(year_text, Text(f"Year: {year_count}", font_size=28).to_corner(UL)),
                run_time=orbit_duration_per_year,
                rate_func=linear
            )
            # At this point, earth_dot is visually back at calendar_zero_marker

            # Determine if this year is a leap year for calculation purposes
            # This logic determines the state *at the end* of the current year_count
            if (year_count % 4 == 0 and year_count % 100 != 0) or (year_count % 400 == 0):
                # This is the year a leap day is added, so the accumulated fraction would hit 1.0
                accumulated_fraction = 1.0 
                is_leap_year_sync_cycle = True
            else:
                # For non-leap years, or years in between that haven't hit the 4th year yet
                # This logic was a bit off, accumulated_fraction should just increment by 0.25
                # and the leap year check above handles the "1.0" case.
                # If it was 0.75 before, it becomes 1.0 ONLY if it's a leap year.
                # Otherwise, it would become 1.0 and then reset in the next non-leap year, which is not right.
                # The accumulated_fraction represents the lag *before* considering the leap day.
                # So, if it's not a leap year, it just accumulates.
                # The `is_leap_year_sync_cycle` will handle the reset.
                
                # Corrected logic:
                if not ((year_count -1) % 4 == 0 and (year_count -1) % 100 != 0) or ((year_count -1) % 400 == 0):
                    # If the *previous* year was NOT a leap year (where it would have reset to 0), then accumulate.
                    # Or, more simply, the accumulation happens, and then a leap year resets it.
                    # Let's simplify: calculate the true accumulated fraction up to this point.
                    # The visual bar should show the state *after* this year's 0.25 day passes.
                    
                    # Simplified accumulation logic:
                    # At the end of each year, 0.25 days are added to the lag,
                    # UNLESS it's a leap year, in which case the lag becomes 1.0 (to be shown then cleared).
                    # The `accumulated_fraction` should reflect the state *before* the leap day adjustment.
                    
                    # Let's track the lag as it builds up.
                    # If previous year was a leap year, current lag starts from 0.25.
                    # If previous year was year 3 of cycle, lag was 0.75, now it's 1.0 (and will be reset).
                    
                    # Revised logic for accumulated_fraction based on year_count in a 4-year cycle
                    # This is the state *after* the current year's orbit but *before* leap day adjustment.
                    current_cycle_year = year_count % 4
                    if current_cycle_year == 1: accumulated_fraction = 0.25
                    elif current_cycle_year == 2: accumulated_fraction = 0.50
                    elif current_cycle_year == 3: accumulated_fraction = 0.75
                    elif current_cycle_year == 0: accumulated_fraction = 1.0 # Year 4 of cycle
                
                is_leap_year_sync_cycle = False # This was set above, ensure it's false if not a leap year.
                if accumulated_fraction == 1.0: # If it naturally hit 1.0, it's a sync cycle.
                    is_leap_year_sync_cycle = True


            # Update accumulated time bar and text
            new_bar_width = day_bar_outline.width * accumulated_fraction
            new_day_bar_fill = Rectangle(width=new_bar_width, height=0.3, color=RED, fill_opacity=0.7).align_to(day_bar_outline, LEFT)
            new_day_bar_fill.move_to(day_bar_outline.get_left(), aligned_edge=LEFT)
            new_accumulated_text = Text(f"{accumulated_fraction:.2f} days", font_size=20).next_to(day_bar_outline, DOWN, buff=0.1, aligned_edge=LEFT)
            
            self.play(
                Transform(day_bar_fill, new_day_bar_fill),
                Transform(accumulated_time_text, new_accumulated_text),
                run_time=0.75
            )
            self.wait(0.2)

            # --- Visualizing Drift or Sync on Orbit Path ---
            # Remove previous drift visuals if they exist
            # Check if mobjects were actually added before trying to remove
            if actual_earth_marker_label.scene == self: self.remove(actual_earth_marker_label)
            if drift_arc_obj.scene == self: self.remove(drift_arc_obj)
            if actual_earth_marker_obj.scene == self: self.remove(actual_earth_marker_obj)
            if drift_text_obj.scene == self: self.remove(drift_text_obj)


            # Visual representation of how far Earth is TRULY ahead of the calendar_zero_marker
            visual_prop_per_quarter_day = 0.04 
            current_visual_drift_prop = (accumulated_fraction / 0.25) * visual_prop_per_quarter_day
            
            actual_earth_end_point = orbit_path.point_from_proportion(current_visual_drift_prop % 1.0)

            # Re-initialize label for current iteration
            actual_earth_marker_label = Text("Earth's Actual Position", font_size=16)

            if accumulated_fraction > 0: 
                drift_arc_obj = ArcBetweenPoints(
                    calendar_zero_marker.get_center(), 
                    actual_earth_end_point, 
                    angle=TAU * current_visual_drift_prop * 0.5, 
                    color=RED
                )
                actual_earth_marker_obj = Dot(color=ORANGE, radius=0.1).move_to(actual_earth_end_point)
                actual_earth_marker_label.next_to(actual_earth_marker_obj, UP, buff=0.1) # Position it
                drift_text_obj = Text(
                    f"Calendar lags by {accumulated_fraction:.2f} days", 
                    font_size=20, color=ORANGE
                ).next_to(orbit_path, DOWN, buff=0.5).shift(LEFT*1.5)

                self.play(
                    Create(drift_arc_obj), 
                    FadeIn(actual_earth_marker_obj), 
                    Write(actual_earth_marker_label),
                    Write(drift_text_obj),
                    run_time=1
                )
                self.add_foreground_mobject(actual_earth_marker_obj) 
            
            if is_leap_year_sync_cycle: # This condition is now more robust
                self.wait(1)
                # Ensure drift_text_obj exists before transforming
                if not drift_text_obj.scene == self : # if it wasn't created (e.g. first year, acc_frac = 0)
                    # This case should not happen if acc_frac is 1.0, so drift_text_obj should exist.
                    # However, for safety, create a placeholder if it's missing.
                    drift_text_obj = Text("",font_size=20).next_to(orbit_path, DOWN, buff=0.5).shift(LEFT*1.5)
                    self.add(drift_text_obj) # Add to scene to be transformable
                
                sync_message1 = Text("Accumulated ~1 full day of lag!", color=YELLOW).move_to(drift_text_obj)
                self.play(Transform(drift_text_obj, sync_message1))
                self.wait(1)
                
                sync_message2 = Text("Leap Day (Feb 29th) added to calendar!", color=GREEN).move_to(sync_message1)
                self.play(Transform(drift_text_obj, sync_message2)) 
                self.wait(0.5)

                # Fade out visuals related to drift
                animations_for_sync = []
                if actual_earth_marker_obj.scene == self: animations_for_sync.append(FadeOut(actual_earth_marker_obj))
                if actual_earth_marker_label.scene == self: animations_for_sync.append(FadeOut(actual_earth_marker_label))
                if drift_arc_obj.scene == self: animations_for_sync.append(Uncreate(drift_arc_obj))
                
                if animations_for_sync:
                    self.play(*animations_for_sync, run_time=1)
                
                # Reset accumulated fraction for the next cycle
                accumulated_fraction = 0.0 # Reset after leap day
                reset_bar_fill = Rectangle(width=0, height=0.3, color=RED, fill_opacity=0.7).align_to(day_bar_outline, LEFT)
                reset_bar_fill.move_to(day_bar_outline.get_left(), aligned_edge=LEFT)
                reset_accumulated_text = Text("0.00 days", font_size=20).next_to(day_bar_outline, DOWN, buff=0.1, aligned_edge=LEFT)
                
                self.play(
                    Transform(day_bar_fill, reset_bar_fill),
                    Transform(accumulated_time_text, reset_accumulated_text),
                    FadeOut(drift_text_obj), 
                    run_time=1
                )
            else: 
                if accumulated_fraction > 0: 
                    self.wait(1.5) 
                    if i < total_years_to_simulate -1:
                        # Prepare list of animations for fading out non-leap year drift visuals
                        fade_out_animations = []
                        if actual_earth_marker_obj.scene == self: fade_out_animations.append(FadeOut(actual_earth_marker_obj))
                        if actual_earth_marker_label.scene == self: fade_out_animations.append(FadeOut(actual_earth_marker_label))
                        if drift_arc_obj.scene == self: fade_out_animations.append(Uncreate(drift_arc_obj))
                        if drift_text_obj.scene == self: fade_out_animations.append(FadeOut(drift_text_obj))
                        if fade_out_animations:
                            self.play(*fade_out_animations, run_time=0.5)

            # Clean up for next loop: ensure they are not in scene if not used or faded.
            # Re-initialize to empty VMobjects to avoid issues if not created in a cycle
            if actual_earth_marker_label.scene == self: self.remove(actual_earth_marker_label)
            if drift_arc_obj.scene == self: self.remove(drift_arc_obj)
            if actual_earth_marker_obj.scene == self: self.remove(actual_earth_marker_obj)
            if drift_text_obj.scene == self: self.remove(drift_text_obj)
            
            drift_arc_obj = VMobject()
            actual_earth_marker_obj = VMobject()
            drift_text_obj = VMobject()
            actual_earth_marker_label = Text("", font_size=16) # Reset for next iteration


        # Final message
        self.wait(1)
        # Clean up any lingering drift visuals from the last iteration if not a leap year
        if actual_earth_marker_label.scene == self: self.remove(actual_earth_marker_label)
        if drift_arc_obj.scene == self: self.remove(drift_arc_obj)
        if actual_earth_marker_obj.scene == self: self.remove(actual_earth_marker_obj)
        if drift_text_obj.scene == self: self.remove(drift_text_obj)

        final_message_1 = Text("Leap years keep our calendar", font_size=28).center().shift(UP*0.5)
        final_message_2 = Text("synchronized with Earth's true orbital position!", font_size=28).next_to(final_message_1, DOWN)
        final_message_group = VGroup(final_message_1, final_message_2)
        
        mobjects_to_fade_finally = Group(*[mob for mob in self.mobjects if mob not in [final_message_group]])
        self.play(FadeOut(mobjects_to_fade_finally, run_time=0.5))
        
        self.play(Write(final_message_group))
        self.wait(3)
        self.play(FadeOut(final_message_group))

