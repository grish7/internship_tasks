--1-Output the number of movies in each category, sorted descending.

SELECT c.name AS category_name, COUNT(fc.film_id) AS movie_count
FROM category c
JOIN film_category fc ON c.category_id = fc.category_id
GROUP BY c.name
ORDER BY movie_count DESC;

--2-Output the 10 actors whose movies rented the most, sorted in descending order.

SELECT a.actor_id, a.first_name, a.last_name, COUNT(r.rental_id) AS rental_count
FROM actor a
JOIN film_actor fa ON a.actor_id = fa.actor_id
JOIN inventory i ON fa.film_id = i.film_id
JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY a.actor_id, a.first_name, a.last_name
ORDER BY rental_count DESC
LIMIT 10;

--3-Output the category of movies on which the most money was spent.

SELECT c.name AS category_name, SUM(p.amount) AS total_spent
FROM category c
JOIN film_category fc ON c.category_id = fc.category_id
JOIN inventory i ON fc.film_id = i.film_id
JOIN rental r ON i.inventory_id = r.inventory_id
JOIN payment p ON r.rental_id = p.rental_id
GROUP BY c.name
ORDER BY total_spent DESC
LIMIT 1;

--4-Print the names of movies that are not in the inventory. Write a query without using the IN operator.

SELECT f.title
FROM film f
LEFT JOIN inventory i ON f.film_id = i.film_id
WHERE i.inventory_id IS NULL;

--5-Output the top 3 actors who have appeared the most in movies in the “Children” category. If several actors have the same number of movies, output all of them.

WITH actor_counts AS (
    SELECT a.actor_id, a.first_name, a.last_name, COUNT(fa.film_id) AS movie_count,
           DENSE_RANK() OVER (ORDER BY COUNT(fa.film_id) DESC) AS ranking
    FROM actor a
    JOIN film_actor fa ON a.actor_id = fa.actor_id
    JOIN film_category fc ON fa.film_id = fc.film_id
    JOIN category c ON fc.category_id = c.category_id
    WHERE c.name = 'Children'
    GROUP BY a.actor_id, a.first_name, a.last_name
)
SELECT first_name, last_name, movie_count
FROM actor_counts
WHERE ranking <= 3;

--6-Output cities with the number of active and inactive customers (active - customer.active = 1). Sort by the number of inactive customers in descending order.

SELECT c.city, 
       SUM(CASE WHEN cu.active = 1 THEN 1 ELSE 0 END) AS active_customers,
       SUM(CASE WHEN cu.active = 0 THEN 1 ELSE 0 END) AS inactive_customers
FROM city c
JOIN address a ON c.city_id = a.city_id
JOIN customer cu ON a.address_id = cu.address_id
GROUP BY c.city_id, c.city
ORDER BY inactive_customers DESC;

--7-Output the category of movies that have the highest number of total rental hours in the city (customer.address_id in this city) and that start with the letter “a”. Do the same for cities that have a “-” in them. Write everything in one query.

WITH city_category_rentals AS (
    SELECT 
        ci.city, 
        c.name AS category_name, 
        ROUND(CAST(SUM(EXTRACT(EPOCH FROM (r.return_date - r.rental_date)) / 3600) AS numeric), 2) AS total_hours,
        ROW_NUMBER() OVER (
            PARTITION BY ci.city_id 
            ORDER BY SUM(EXTRACT(EPOCH FROM (r.return_date - r.rental_date)) / 3600) DESC
        ) AS rn
    FROM city ci
    JOIN address a ON ci.city_id = a.city_id
    JOIN customer cu ON a.address_id = cu.address_id
    JOIN rental r ON cu.customer_id = r.customer_id
    JOIN inventory i ON r.inventory_id = i.inventory_id
    JOIN film_category fc ON i.film_id = fc.film_id
    JOIN category c ON fc.category_id = c.category_id
    WHERE r.return_date IS NOT NULL 
    GROUP BY ci.city_id, ci.city, c.name
)
SELECT 'Starts with A' AS city_group, city, category_name, total_hours
FROM city_category_rentals
WHERE city LIKE 'A%' AND rn = 1

UNION ALL

SELECT 'Contains hyphen' AS city_group, city, category_name, total_hours
FROM city_category_rentals
WHERE city LIKE '%-%' AND rn = 1;


