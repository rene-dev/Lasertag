rotate(90, [1, 0, 0])
{
difference()
{
	// the whole platform
	intersection()
	{
		cube([50, 5, 50], center = true);
		rotate(45, [0, 1, 0])
			cube([60, 5, 60], center = true);
	}
	for(i=[0:3])
	{
		rotate(i*90, [0, 1, 0])
		{
			// ir recv pin holes
			translate([19, 0, 19])
				rotate(45, [0, 1, 0])
					cube([7, 5, 3], center = true);

			translate([23, 0.75, 23])
				intersection()
				{
					rotate(45, [0, 1, 0])
						cube([20, 3.5, 9], center = true);
				}

			// led pin holes
			translate([0, 0, 21])
				cube([9, 5, 3], center = true);
		}
	}

	difference()
	{
		// big hole in the center
		intersection()
		{
			cube([36, 5, 36], center = true);
			rotate(45, [0, 1, 0])
				cube([48, 5, 48], center = true);
		}
		// led platforms
		for(i=[0:3])
		{
			rotate(i*90, [0, 1, 0])
			{
				translate([0, 0, 21])
					rotate(90, [1, 0, 0])
						cylinder(r = 10/2, h = 5, center = true, $fn = 360);
			}
		}
	}

	// capacitor
	translate([16.5, 0, 10])
		rotate(90, [1, 0, 0])
			cylinder(r = 8/2, h = 6, center = true, $fn = 360);
}
}