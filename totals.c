#include <stdio.h>
#include <stdlib.h>
#include <gmp.h>

void gcd(mpz_t result, const mpz_t u, const mpz_t v) {
    mpz_gcd(result, u, v);
}

void euler_totient(mpz_t result, const mpz_t n) {
    mpz_t i, temp_n;
    mpz_inits(i, temp_n, NULL);
    mpz_set(temp_n, n);
    mpz_set(result, n);

    for (mpz_set_ui(i, 2); mpz_cmp(i, temp_n) <= 0; mpz_add_ui(i, i, 1)) {
        if (mpz_divisible_p(temp_n, i)) {
            while (mpz_divisible_p(temp_n, i)) {
                mpz_divexact(temp_n, temp_n, i);
            }
            mpz_t quotient;
            mpz_init(quotient);
            mpz_fdiv_q(quotient, result, i);
            mpz_sub(result, result, quotient);
            mpz_clear(quotient);
        }
    }

    if (mpz_cmp_ui(temp_n, 1) > 0) {
        mpz_t quotient;
        mpz_init(quotient);
        mpz_fdiv_q(quotient, result, temp_n);
        mpz_sub(result, result, quotient);
        mpz_clear(quotient);
    }

    mpz_clears(i, temp_n, NULL);
}

void comb(mpz_t result, mpz_t n, const mpz_t k) {
    mpz_t temp_k, numerator, denominator, i;
    mpz_inits(temp_k, numerator, denominator, i, NULL);

    mpz_set_ui(result, 1);
    mpz_sub(temp_k, n, k);

    for (mpz_set_ui(i, 1); mpz_cmp(i, k) <= 0; mpz_add_ui(i, i, 1)) {
        mpz_mul(result, result, n);
        mpz_divexact(result, result, i);
        mpz_sub_ui(n, n, 1);  // No longer const, so can modify
    }

    mpz_clears(temp_k, numerator, denominator, i, NULL);
}

void N(mpz_t result, const mpz_t n, const mpz_t d) {
    mpz_t gcd_n_d, total, j, temp_result, temp_comb, n_div_j, d_div_j;
    mpz_inits(gcd_n_d, total, j, temp_result, temp_comb, n_div_j, d_div_j, NULL);

    gcd(gcd_n_d, n, d);
    mpz_set_ui(total, 0);

    for (mpz_set_ui(j, 1); mpz_cmp(j, gcd_n_d) <= 0; mpz_add_ui(j, j, 1)) {
        if (mpz_divisible_p(gcd_n_d, j)) {
            euler_totient(temp_result, j);
            mpz_tdiv_q(n_div_j, n, j);
            mpz_tdiv_q(d_div_j, d, j);
            comb(temp_comb, n_div_j, d_div_j);
            mpz_mul(temp_result, temp_result, temp_comb);
            mpz_add(total, total, temp_result);
        }
    }

    mpz_tdiv_q(result, total, n);

    mpz_clears(gcd_n_d, total, j, temp_result, temp_comb, n_div_j, d_div_j, NULL);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <EDO>\n", argv[0]);
        return 1;
    }

    mpz_t EDO, d, result, total;
    mpz_inits(EDO, d, result, total, NULL);

    mpz_set_str(EDO, argv[1], 10);
    mpz_set_ui(total, 0);  // Initialize total to 0

    for (mpz_set_ui(d, 0); mpz_cmp(d, EDO) <= 0; mpz_add_ui(d, d, 1)) {
        N(result, EDO, d);
        gmp_printf("N(%Zd, %Zd) = %Zd\n", EDO, d, result);
        mpz_add(total, total, result);  // Add each result to the total
    }

    // Print the total
    gmp_printf("N(%Zd) = %Zd\n", EDO, total);

    mpz_clears(EDO, d, result, total, NULL);
    return 0;
}