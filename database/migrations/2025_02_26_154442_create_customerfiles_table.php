<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('customerfiles', function (Blueprint $table) {
            $table->id();
            $table->string('customername');
            $table->string('deliveryaddress')->nullable();
            $table->string('deliveryremarks')->nullable();
            $table->decimal('deliverycharge',total: 10, places: 2)->nullable();
            $table->bigInteger('phonenumber');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('customerfiles');
    }
};
